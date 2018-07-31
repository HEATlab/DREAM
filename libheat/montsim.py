import numpy as np

from . import srea
from . import functiontimer
from . import printers as pr

Z_NODE_ID = 0


class Simulator(object):
    def __init__(self, random_seed=None):
        # Nothing here for now.
        self.stn = None
        self.assignment_stn = None
        self._current_time = 0.0

        self._ar_contingent_event_counter = 0
        self._rand_seed = random_seed
        self._rand_state = np.random.RandomState(random_seed)
        self.num_reschedules = 0
        self.num_sent_schedules = 0

    def simulate(self, starting_stn, execution_strat, sim_options={}):
        '''Run one simulation.

        Args:
            starting_stn (STN): The STN used to run in the simulation.
            execution_strat (str): The strategy to use for timepoint execution.
                Acceptable execution strategies include--
                "early",
                "drea",
                "drea-si",
                "drea-ar",
                "arsi"
            sim_options (dict, optional): A dictionary of possible options to
                pass into the simulator.

        Returns:
            Boolean indicating whether the simulation was successful or not.
        '''
        # Initial setup
        self._current_time = 0.0
        self.stn = starting_stn.copy()
        self.assignment_stn = starting_stn.copy()
        self._ar_contingent_event_counter = 0
        self._ara_successfactor = 1.0
        self.num_reschedules = 0
        self.num_sent_schedules = 0
        # Resample the contingent edges.
        # Super important!
        pr.verbose("Resampling Stored STN")
        self.resample_stored_stn()

        # Setup options
        first_run = True
        options = {"first_run": True,
                   "executed_contingent": False,
                   "executed_time": 0.0,
                   "guide_min": 0.0,
                   "guide_max": 0.0}
        if "si_threshold" in sim_options:
            options["si_threshold"] = sim_options["si_threshold"]
        if "ar_threshold" in sim_options:
            options["ar_threshold"] = sim_options["ar_threshold"]
        if "alp_threshold" in sim_options:
            options["alp_threshold"] = sim_options["alp_threshold"]

        # Setup default guide settings
        guide_stn = self.stn
        current_alpha = 0.0

        # Loop until all timepoints assigned.
        while not self.all_assigned():
            options["first_run"] = first_run
            if first_run:
                first_run = False

            # Calculate the guide STN.
            pr.vverbose("Getting Guide...")
            functiontimer.start("get_guide")
            current_alpha, guide_stn = self.get_guide(execution_strat,
                                                      current_alpha,
                                                      guide_stn,
                                                      options=options)
            #print("GUIDE")
            #print(guide_stn)
            functiontimer.stop("get_guide")
            pr.vverbose("Got guide")

            # Select the next timepoint.
            pr.vverbose("Selecting timepoint...")
            functiontimer.start("selection")
            selection = self.select_next_timepoint(guide_stn,
                                                   self._current_time)
            functiontimer.stop("selection")
            pr.vverbose("Selected timepoint, node_id of {}"
                        .format(selection[0]))

            next_vert_id = selection[0]
            next_time = selection[1]
            executed_contingent = selection[2]

            options["executed_contingent"] = executed_contingent
            options["executed_time"] = next_time
            options["guide_max"] = guide_stn.get_edge_weight(0, next_vert_id)
            options["guide_min"] = -guide_stn.get_edge_weight(next_vert_id, 0)

            # Propagate constraints (minimise) and check consistency.
            pr.verbose("Prior to placement STN:\n{}".format(self.stn))
            pr.verbose("guide STN:\n{}".format(guide_stn))
            self.assign_timepoint(guide_stn, next_vert_id, next_time)
            self.assign_timepoint(self.stn, next_vert_id, next_time)
            self.assign_timepoint(self.assignment_stn, next_vert_id, next_time)
            functiontimer.start("propagation & check")
            stn_copy = self.stn.copy()
            consistent = self.propagate_constraints(stn_copy)
            if not consistent:
                pr.verbose("Assignments: " + str(self.get_assigned_times()))
                pr.verbose("Failed to place point {}, at {}"
                           .format(next_vert_id, next_time))
                return False
            self.stn = stn_copy
            pr.vverbose("Done propagating our STN")
            functiontimer.stop("propagation & check")

            # Clean up the STN
            self.remove_old_timepoints(self.stn)

            self._current_time = next_time
        pr.verbose("Assignments: " + str(self.get_assigned_times()))
        pr.verbose("Successful!")
        assert (self.propagate_constraints(self.assignment_stn))
        return True

    def select_next_timepoint(self, dispatch, current_time):
        """Retrieves the earliest possible vert.

        Ties are broken arbitrarily.

        Args:
            dispatch: STN which is used for getting the right dispatch.
            current_time: Current time of the simulation.

        Returns:
            Returns a tuple of (vert, time) where 'vert' is the vert ID
            of the vert which has the earliest assignment time, and 'time'
            If no timepoint can be selected, returns (None, inf)
        """
        earliest_so_far = None
        earliest_so_far_time = float("inf")
        has_incoming_contingent = False

        # This could be sped up. We only want unexecuted verts without parents.
        for i, vert in dispatch.verts.items():
            # Don't recheck already executed verts
            if vert.is_executed():
                continue
            # Check if all predecessors are executed -> enabled.
            predecessor_ids = [e.i for e in dispatch.get_incoming(i)]
            predecessors = [dispatch.get_vertex(q) for q in predecessor_ids]
            is_enabled = all([p.is_executed() for p in predecessors])
            # Exit early if not enabled.
            if not is_enabled:
                continue
            incoming_contingent = dispatch.get_incoming_contingent(i)
            if incoming_contingent is None:
                # Get the
                # Make sure that we can't go back in time though.
                incoming_reqs = dispatch.get_incoming(i)
                if incoming_reqs == []:
                    # No incoming edges at all, this will be our start.
                    earliest_time = 0.0
                else:
                    earliest_time = max([edge.get_weight_min()
                                         + self.stn.get_assigned_time(edge.i)
                                         for edge in incoming_reqs])
            else:
                sample_time = incoming_contingent.sampled_time()
                # Get the contingent edge's predecessor
                cont_pred = incoming_contingent.i
                assigned_time = dispatch.get_assigned_time(cont_pred)
                if assigned_time is None:
                    # This is an incredibly bizarre edge case that SREA
                    # sometimes produces: It alters the assigned points to
                    # an invalid time. One work around is to manually find the
                    # UPPER bound (not the lower bound), because that appears
                    # untouched by SREA.
                    pr.warning("Executed event was not assigned.")
                    pr.warning("Event was: {}".format(cont_pred))
                    vert = dispatch.get_vertex(cont_pred)
                    new_time = dispatch.get_edge_weight(Z_NODE_ID,
                                                        cont_pred)
                    msg = "Re-assigned to: {}".format(new_time)
                    pr.warning(msg)
                    earliest_time = new_time
                else:
                    earliest_time = dispatch.get_assigned_time(cont_pred) \
                        + sample_time
            # Update the earliest time  now.
            if earliest_so_far_time > earliest_time:
                earliest_so_far = i
                earliest_so_far_time = earliest_time
                has_incoming_contingent = (incoming_contingent is not None)
        return (earliest_so_far, earliest_so_far_time,
                has_incoming_contingent)

    def assign_timepoint(self, stn, vert_id, time):
        """Assigns a timepoint to specified time

        Args:
            stn (STN): STN to assign on.
            vert_id (int): Node to assign.
            time (float): Time to assign to this vert.

        Post:
            stn is modified in-place to have an assigned vertex.
        """
        if vert_id != Z_NODE_ID:
            stn.update_edge(Z_NODE_ID,
                            vert_id,
                            time,
                            create=True,
                            force=True)
            stn.update_edge(vert_id,
                            Z_NODE_ID,
                            -time,
                            create=True,
                            force=True)
        stn.get_vertex(vert_id).execute()

    def propagate_constraints(self, stn_to_prop):
        """ Updates current constraints and minimises
        """
        functiontimer.start("propogate_constraints")
        ans = stn_to_prop.floyd_warshall()
        functiontimer.stop("propogate_constraints")
        return ans

    def all_assigned(self) -> bool:
        """ Check if all vertices of the STN have been executed.
        Returns:
            Boolean indicated whether all vertices in the assignment STN have
            been executed.
        """
        for vert in self.assignment_stn.get_all_verts():
            if not vert.is_executed():
                return False
        return True

    def remove_old_timepoints(self, stn) -> None:
        """ Remove timepoints which add no new information, as they exist
        entirely in the past, and have no lingering constraints that are not
        already captured.
        """
        stored_keys = list(stn.verts.keys())
        for v_id in stored_keys:
            if v_id == 0:
                continue
            if (stn.outgoing_executed(v_id) and
                    stn.get_vertex(v_id).is_executed()):
                stn.remove_vertex(v_id)

    def resample_stored_stn(self) -> None:
        """Resample the stored STN contingent edges (self.stn)"""
        for e in self.stn.contingent_edges.values():
            e.resample(self._rand_state)

    def get_assigned_times(self) -> dict:
        """Return when each timepoint in the simulation was assigned"""
        times = {}
        for key, v in self.assignment_stn.verts.items():
            if v.is_executed():
                times[key] = (self.assignment_stn.get_assigned_time(key))
            else:
                times[key] = (None)
        return times

    def get_guide(self, execution_strat, previous_alpha,
                  previous_guide, options={}) -> tuple:
        """ Retrieve a guide STN (dispatch) based on the execution strategy

        Args:
            execution_strat (str): String representing the execution strategy.
            previous_alpha (float): The previously used guide STN's alpha.
            previous_guide (STN): The previously used guide STN.
            options (dict, optional): Dictionary of possible options to use for
                the algorithms.

        Return:
            Returns a tuple with format:
            | [0]: Alpha of the guide.
            | [1]: dispatch (type STN) which the simulator should follow,
        """
        if execution_strat == "early":
            return 1.0, self.stn
        elif execution_strat == "srea":
            return self._srea_algorithm(previous_alpha,
                                        previous_guide,
                                        options["first_run"])
        elif execution_strat == "drea":
            return self._drea_algorithm(previous_alpha,
                                        previous_guide,
                                        options["first_run"],
                                        options["executed_contingent"])
        elif execution_strat == "drea-s":
            return self._drea_s_algorithm(previous_alpha,
                                          previous_guide,
                                          options["first_run"],
                                          options["executed_contingent"],
                                          options["executed_time"],
                                          options["guide_min"],
                                          options["guide_max"])
        elif execution_strat == "drea-si":
            return self._drea_si_algorithm(previous_alpha,
                                           previous_guide,
                                           options["first_run"],
                                           options["executed_contingent"],
                                           options["si_threshold"])
        elif execution_strat == "drea-alp":
            return self._drea_alp_algorithm(previous_alpha,
                                            previous_guide,
                                            options["first_run"],
                                            options["executed_contingent"],
                                            options["alp_threshold"])
        elif execution_strat == "drea-ar":
            if options["executed_contingent"]:
                self._ar_contingent_event_counter += 1
            ans = self._drea_ar_algorithm(previous_alpha,
                                          previous_guide,
                                          options["first_run"],
                                          options["executed_contingent"],
                                          options["ar_threshold"],
                                          self._ar_contingent_event_counter)
            self._ar_contingent_event_counter = ans[2]
            return ans[0], ans[1]
        elif execution_strat == "drea-ara":
            if not options["executed_contingent"] and not options["first_run"]:
                return previous_alpha, previous_guide
            in_bounds = (options["guide_min"] <= options["executed_time"]
                         <= options["guide_max"])
            pr.verbose("In bounds?: {}".format(in_bounds))
            pr.verbose("{}, {}, {}".format(options["guide_min"],
                                               options["executed_time"],
                                               options["guide_max"]))
            ans = self._drea_ara_algorithm(previous_alpha,
                                           previous_guide,
                                           options["first_run"],
                                           options["ar_threshold"],
                                           self._ara_successfactor,
                                           in_bounds)
            self._ara_successfactor = ans[2]
            return ans[0], ans[1]
        elif execution_strat == "arsi":
            if options["executed_contingent"]:
                self._ar_contingent_event_counter += 1
            ans = self._arsi_algorithm(previous_alpha,
                                       previous_guide,
                                       options["first_run"],
                                       options["executed_contingent"],
                                       self._ar_contingent_event_counter,
                                       ar_threshold=options["ar_threshold"],
                                       si_threshold=options["si_threshold"])
            self._ar_contingent_event_counter = ans[2]
            return ans[0], ans[1]
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(execution_strat))

    def _srea_wrapper(self, previous_alpha, previous_guide):
        """ Small wrapper to run SREA or keep the same guide if it's not
            consistent.
        """
        self.num_reschedules += 1
        result = srea.srea(self.stn)
        if result is not None:
            self.num_sent_schedules += 1
            return result[0], result[1]
        # Our guide was inconsistent... um. Well.
        # This is not great.
        # Follow the previous guide?
        return previous_alpha, previous_guide

    def _srea_algorithm(self, previous_alpha, previous_guide, first_run):
        """ Implements the SREA algorithm. """
        if first_run:
            return self._srea_wrapper(previous_alpha, previous_guide)
        # Not our first run, use the previous guide.
        return previous_alpha, previous_guide

    def _drea_algorithm(self, previous_alpha, previous_guide, first_run,
                        executed_contingent):
        """ Implements the DREA algorithm. """
        if first_run or executed_contingent:
            ans = self._srea_wrapper(previous_alpha, previous_guide)
            pr.verbose("DREA Rescheduled, new alpha: {}".format(ans[0]))
            return ans
        return previous_alpha, previous_guide

    def _drea_s_algorithm(self, previous_alpha, previous_guide, first_run,
                         executed_contingent, next_time, min_time, max_time):
        """ Implements the SREA-S algorithm. """
        if first_run:
            return self._srea_wrapper(previous_alpha, previous_guide)
        if executed_contingent:
            if (not (min_time <= next_time <= max_time)):
                pr.verbose("Rescheduling! t={}, not in [{}, {}]"
                           .format(next_time, min_time, max_time))
                # We need to reschedule now.
                return self._srea_wrapper(previous_alpha, previous_guide)
            pr.verbose("Did not reschedule, t={} in [{}, {}]"
                        .format(next_time, min_time, max_time))
        return previous_alpha, previous_guide

    def _drea_si_algorithm(self, previous_alpha, previous_guide, first_run,
                           executed_contingent, threshold):
        """ Implements the DREA-SI algorithm. """
        # Exit early if the STN was not consistent at all.

        if first_run:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            self.num_sent_schedules += 1
            if result is None:
                return previous_alpha, previous_guide
            new_alpha = result[0]
            maybe_guide = result[1]
            pr.verbose("Got new drea-si guide with alpha={}".format(new_alpha))
            return new_alpha, maybe_guide
        # We should only run this algorithm *if* we recently executed
        # a receieved/contingent timepoint.
        if not executed_contingent:
            return previous_alpha, previous_guide
        # Reschedule
        result = srea.srea(self.stn)
        self.num_reschedules += 1
        if result is None:
            return previous_alpha, previous_guide
        new_alpha = result[0]
        maybe_guide = result[1]

        # num_cont : Number of remaining unexecuted contingent events
        num_cont = self.remaining_contingent_count(maybe_guide)
        p_0 = (1-previous_alpha)**num_cont
        p_1 = (1-new_alpha)**num_cont
        if p_1 - p_0 > threshold:
            self.num_sent_schedules += 1
            pr.verbose("Got new drea-si guide with alpha={}".format(new_alpha))
            return new_alpha, maybe_guide
        else:
            pr.verbose("Did not reschedule, p_0={}, p_1={}".format(p_0, p_1))
            return previous_alpha, previous_guide

    def _drea_alp_algorithm(self, previous_alpha, previous_guide, first_run,
                            executed_contingent, threshold):
        """ Implements the DREA alpha difference algorithm, which is an attempt
        to correct DREA-SI which has a fatal flaw of not rescheduling when
        contingent events tend to differ.
        """
        if first_run:
            self.num_reschedules += 1
            result = srea.srea(self.stn)
            if result is None:
                return previous_alpha, previous_guide
            new_alpha = result[0]
            maybe_guide = result[1]
            self.num_sent_schedules += 1
            pr.verbose("Got new drea-alp guide with alpha={}"
                       .format(new_alpha))
            return new_alpha, maybe_guide
        # We should only run this algorithm *if* we recently executed
        # a receieved/contingent timepoint.
        if not executed_contingent:
            return previous_alpha, previous_guide
        # We are therefore actually running the algorithm.
        result = srea.srea(self.stn)
        self.num_reschedules += 1
        if result is None:
            return previous_alpha, previous_guide
        new_alpha = result[0]
        maybe_guide = result[1]
        # num_cont : Number of remaining unexecuted contingent events
        num_cont = 0
        for i in maybe_guide.received_timepoints:
            if not maybe_guide.get_vertex(i).is_executed():
                num_cont += 1

        if abs(new_alpha - previous_alpha) > threshold:
            pr.verbose("Got new drea-alp guide with alpha={}"
                       .format(new_alpha))
            self.num_sent_schedules += 1
            return new_alpha, maybe_guide
        else:
            pr.verbose("Did not send reschedule, a0={}, a1={}"
                       .format(previous_alpha, new_alpha))
            return previous_alpha, previous_guide

    def _drea_ar_algorithm(self, previous_alpha, previous_guide, first_run,
                           executed_contingent, threshold,
                           contingent_event_counter):
        """ Implements the DREA-AR algorithm. """
        if first_run:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            if result is not None:
                self.num_sent_schedules += 1
                return result[0], result[1], contingent_event_counter
            else:
                return previous_alpha, previous_guide, contingent_event_counter
        # We should only run this algorithm *if* we recently executed
        # a receieved/contingent timepoint.
        if not executed_contingent:
            return previous_alpha, previous_guide, contingent_event_counter

        # n is a placeholder for how much uncertainty we can take.
        n = 0
        if threshold == 0:
            n = float("inf")
        else:
            while (1-previous_alpha)**(n+1) > threshold and attempts < 100:
                n += 1

        # Temporary variable to maintain unique names.
        new_counter = contingent_event_counter
        if contingent_event_counter >= n:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            if result is not None:
                pr.verbose("DREA-AR rescheduled our STN")
                new_alpha = result[0]
                maybe_guide = result[1]
                new_counter = 0
                self.num_sent_schedules += 1
                return new_alpha, maybe_guide, new_counter
        return previous_alpha, previous_guide, new_counter

    def _drea_ara_algorithm(self, previous_alpha, previous_guide, first_run,
                            threshold, successfactor, in_bounds):
        """ Implements the DREA-ARA algorithm.

        Written by Jordan...
        Oh god please, this function's arguments are cancer. -Jordan 2018
        """
        if first_run:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            if result is not None:
                self.num_sent_schedules += 1
                return result[0], result[1], successfactor
            else:
                return previous_alpha, previous_guide, successfactor

        # Temporary variable to maintain unique names.
        newfactor = successfactor
        if in_bounds:
            newfactor *= 1.0-previous_alpha
        else:
            newfactor = min(1.0-previous_alpha, previous_alpha/2.0)

        if successfactor <= threshold:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            if result is not None:
                pr.verbose("DREA-AR rescheduled our STN")
                new_alpha = result[0]
                maybe_guide = result[1]
                newfactor = 1.0
                self.num_sent_schedules += 1
                return new_alpha, maybe_guide, newfactor
        return previous_alpha, previous_guide, newfactor

    def _arsi_algorithm(self, previous_alpha, previous_guide, first_run,
                        executed_contingent, contingent_event_counter,
                        ar_threshold=0.0,
                        si_threshold=0.0):
        """Implements the ARSI algorithm. This is now technically ARSC, not
        ARSI anymore because we are doing a direct alpha comparsion.

        Direct alpha comparison with absolute value allows considering cases
        where we *do* see an increase in risk, rather than a decrease.
        """
        if first_run:
            result = srea.srea(self.stn)
            self.num_reschedules += 1
            if result is not None:
                self.num_sent_schedules += 1
                new_alpha = result[0]
                new_guide = result[1]
                return new_alpha, new_guide, contingent_event_counter
            return previous_alpha, previous_guide, contingent_event_counter
        # We should only run this algorithm *if* we recently executed
        # a receieved/contingent timepoint.
        if not executed_contingent:
            return previous_alpha, previous_guide, contingent_event_counter
        # AR SECTION ----------------------------------------------------------
        # n is a placeholder for how much uncertainty we can take.
        n = 0
        attempts = 0  # Make sure we can actually escape if threshold = 0
        while (1-previous_alpha)**(n+1) > ar_threshold and attempts < 100:
            n += 1
            attempts += 1
        # Should we reschedule?
        result = None
        if contingent_event_counter >= n:
            # Get a new schedule
            pr.verbose("ARSC rescheduled...")
            result = srea.srea(self.stn)
            self.num_reschedules += 1
        if result is None:
            # Early exit if SREA failed OR if it's not time yet to reschedule
            return previous_alpha, previous_guide, contingent_event_counter
        # SI SECTION ----------------------------------------------------------
        new_alpha = result[0]
        maybe_guide = result[1]

        num_cont = self.remaining_contingent_count(maybe_guide)
        if abs(new_alpha - previous_alpha) >= si_threshold:
            self.num_sent_schedules += 1
            pr.verbose("Got new ARSC guide with alpha={}".format(new_alpha))
            return new_alpha, maybe_guide, 0
        else:
            pr.verbose(("ARSC did not send schedule, previous_alpha={}, "
                       +"new_alpha={}")
                       .format(previous_alpha, new_alpha))
            return previous_alpha, previous_guide, contingent_event_counter
        return previous_alpha, previous_guide, contingent_event_counter

    def remaining_contingent_count(self, stn):
        """Returns the number of remaining (unexecuted) contingent events"""
        # num_cont : Number of remaining unexecuted contingent events
        num_cont = 0
        for i in stn.received_timepoints:
            if not stn.get_vertex(i).is_executed():
                num_cont += 1
        return num_cont
