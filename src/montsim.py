import random
import numpy as np

import srea
import functiontimer
import printers as pr


Z_NODE_ID = 0


class Simulator(object):
    def __init__(self, random_seed=None):
        # Nothing here for now.
        self.stn = None
        self._current_time = 0.0

        self._rand_state = np.random.RandomState(random_seed)

    def simulate(self, starting_stn, execution_strat, sim_options={}):
        ''' Run one simulation.

        Args:
            starting_stn: The STN used to run in the simulation.
            execution_strat: String representing the strategy to use for
                timepoint execution. Acceptable execution strategies include--
                "early",
                "drea",
                "d-drea",
                "drea-si",
                "drea-ar"

        Keyword Args:
            sim_options: A dictionary of possible options to pass into the

        Returns:
            Boolean indicating whether the simulation was successful or not.
        '''
        # Initial setup
        self._current_time = 0.0
        self.stn = starting_stn.copy()
        self._ar_contingent_event_counter = 0
        # Resample the contingent edges.
        # Super important!
        pr.verbose("Resampling Stored STN")
        self.resample_stored_stn()

        # Setup options
        first_run = True
        options = {"first_run": True,
                   "executed_contingent": False}
        if "threshold_si" in sim_options:
           options["threshold_si"] = sim_options["threshold_si"]
        if "threshold_ar" in sim_options:
           options["threshold_ar"] = sim_options["threshold_ar"]

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
            functiontimer.start_timer("get_guide")
            current_alpha, guide_stn = self.get_guide(execution_strat,
                                                      current_alpha,
                                                      guide_stn,
                                                      options=options)
            functiontimer.stop_timer("get_guide")
            pr.vverbose("Got guide")

            # Select the next timepoint.
            pr.vverbose("Selecting timepoint...")
            functiontimer.start_timer("selection")
            selection = self.select_next_timepoint(guide_stn,
                                                   self._current_time)
            functiontimer.stop_timer("selection")
            pr.vverbose("Selected timepoint, node_id of {}"
                        .format(selection[0]))

            next_vert_id = selection[0]
            next_time = selection[1]
            executed_contingent = selection[2]

            options['executed_contingent'] = executed_contingent

            # Propagate constraints (minimise) and check consistency.
            self.assign_timepoint(guide_stn, next_vert_id, next_time)
            self.assign_timepoint(self.stn, next_vert_id, next_time)
            consistent = self.propagate_constraints(self.stn.copy())
            if not consistent:
                pr.verbose("Failed to place point {}, at {}"
                           .format(next_vert_id, next_time))
                return False
            pr.vverbose("Propagating our STN")
            self.propagate_constraints(self.stn)
            pr.vverbose("Done propagating our STN")
            self._current_time = next_time
        return True

    def select_next_timepoint(self, dispatch, current_time):
        """ Retrieves the earliest possible vert.
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
        for i, vert in enumerate(dispatch.get_all_verts()):
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
                    earliest_time = 0.0
                else:
                    earliest_time = max([edge.get_weight_min()
                                         + self.stn.get_assigned_time(edge.i)
                                         for edge in incoming_reqs])
            else:
                sample_time = incoming_contingent.sampled_time()
                contingent_pred = incoming_contingent.i
                earliest_time = dispatch.get_assigned_time(contingent_pred) \
                    + sample_time
            # Update the earliest time  now.
            if earliest_so_far_time > earliest_time:
                earliest_so_far = i
                earliest_so_far_time = earliest_time
                has_incoming_contingent = (incoming_contingent is None)

        return (earliest_so_far, earliest_so_far_time,
                has_incoming_contingent)

    def assign_timepoint(self, stn, vert_id, time):
        """ Assigns a timepoint to specified time

        Args:
            vert: Node to assign.
            time: float: Time to assign this vert.
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
        functiontimer.start_timer("propogate_constraints")
        ans = stn_to_prop.floyd_warshall()
        functiontimer.stop_timer("propogate_constraints")
        return ans

    def all_assigned(self) -> bool:
        """ Check if all vertices of the STN have been assigned
        """
        for vert in self.stn.get_all_verts():
            if not vert.is_executed():
                return False
        return True

    def remove_old_timepoints(self) -> None:
        """ Remove timepoints which add no new information, as they exist
        entirely in the past, and have no lingering constraints that are not
        already captured.
        """
        for v_id in range(len(self.stn.get_all_verts())):
            if self.stn.outgoing_executed(v_id):
                self.stn.remove_vertex(v_id)

    def resample_stored_stn(self) -> None:
        for e in self.stn.contingent_edges.values():
            e.resample(self._rand_state)

    def get_assigned_times(self) -> dict:
        times = {}
        for key, v in self.stn.verts.items():
            if v.is_executed():
                times[key] = (self.stn.get_assigned_time(key))
            else:
                times[key] = (None)
        return times

    def get_guide(self, execution_strat, previous_alpha,
                  previous_guide, options={}) -> tuple:
        """ Retrieve a guide STN (dispatch) based on the execution strategy
        Args:
            execution_strat: String representing the execution strategy.
            previous_: The previously used guide STN's alpha.
            previous_guide: The previously used guide STN.

        Keyword Args:
            options: Dictionary of possible options to use for the algorithms.

        Return:
            Returns a tuple with format:
            [0]: Alpha of the guide.
            [1]: dispatch (type STN) which the simulator should follow,
        """
        if execution_strat == "early":
            return 1.0, self.stn
        if execution_strat == "srea":
            return self._srea_algorithm(previous_alpha,
                                        previous_guide,
                                        options["first_run"])
        if execution_strat == "drea":
            return self._drea_algorithm(previous_alpha,
                                        previous_guide,
                                        options["first_run"],
                                        options["executed_contingent"])
        if execution_strat == "drea-si":
            return self._drea_si_algorithm(previous_alpha,
                                           previous_guide,
                                           options["first_run"],
                                           options["threshold_si"])
        if execution_strat == "drea-ar":
            if options["executed_contingent"]:
                self._ar_contingent_event_counter += 1
            ans = self._drea_ar_algorithm(previous_alpha,
                                          previous_guide,
                                          options["first_run"],
                                          options["threshold_ar"],
                                          self._ar_contingent_event_counter)
            self._ar_contingent_event_counter = ans[2]
            return ans[0], ans[1]
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(execution_strat))

    def _srea_wrapper(self, previous_alpha, previous_guide):
        """ Small wrapper to run SREA or keep the same guide if it's not
            consistent.
        """
        result = srea.srea(self.stn)
        if result is not None:
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
            return self._srea_wrapper(previous_alpha, previous_guide)
        return previous_alpha, previous_guide

    def _drea_si_algorithm(self, previous_alpha, previous_guide, first_run,
                           threshold):
        """ Implements the DREA-SI algorithm. """
        result = srea.srea(self.stn)
        # Exit early if the STN was not consistent at all.
        if result is None:
            return previous_alpha, previous_guide

        new_alpha = result[0]
        maybe_guide = result[1]
        if first_run:
            pr.verbose("Got new drea-si guide with alpha={}".format(new_alpha))
            return new_alpha, maybe_guide

        # num_cont : Number of remaining unexecuted contingent events
        num_cont = 0
        for i in maybe_guide.received_timepoints:
            if not maybe_guide.get_vertex(i).is_executed():
                num_cont += 1

        p_0 = (1-previous_alpha)**num_cont
        p_1 = (1-new_alpha)**num_cont
        if p_1 - p_0 > threshold:
            pr.verbose("Got new drea-si guide with alpha={}".format(new_alpha))
            return new_alpha, maybe_guide
        else:
            pr.verbose("Did not reschedule, p_0={}, p_1={}".format(p_0, p_1))
            return previous_alpha, previous_guide

    def _drea_ar_algorithm(self, previous_alpha, previous_guide, first_run,
                           threshold, contingent_event_counter):
        """ Implements the DREA-AR algorithm. """
        if first_run:
            result = srea.srea(self.stn)
            if result is not None:
                return result[0], result[1], contingent_event_counter

        # n is a placeholder for how much uncertainty we can take.
        n = 0
        while (1-previous_alpha)**(n+1) > threshold:
            n += 1

        # Temporary variable to maintain unique names.
        new_counter = contingent_event_counter
        if contingent_event_counter >= n or first_run:
            result = srea.srea(self.stn)
            if result is not None:
                pr.verbose("DREA-AR rescheduled our STN")
                new_alpha = result[0]
                maybe_guide = result[1]
                new_counter = 0
                return new_alpha, maybe_guide, new_counter
        return previous_alpha, previous_guide, new_counter
