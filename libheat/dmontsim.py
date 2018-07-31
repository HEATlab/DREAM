import numpy as np


from .montsim import Simulator
from .decoupling import optdecouple
from .decoupling import sreadecouple
from . import srea
from . import functiontimer
from . import printers as pr


Z_NODE_ID = 0


class DecoupledSimulator(Simulator):

    def simulate(self, starting_stn, decouple_type="opt_inter",
                 sim_options={}) -> bool:
        """Run one simulation.

        Args:
            starting_stn (:obj:`STN`): The STN used to run in the simulation.
            decouple_type (str): The decoupling strategy. Default is
                "opt_inter". "srea" is also an acceptable input.
            sim_options (:obj:`dict`, optional): A dictionary of possible
                options to pass into the

        Returns:
            Boolean indicating whether the simulation was successful or not.
        """
        # Initial setup
        self._current_time = 0.0
        self.stn = starting_stn.copy()
        self.assignment_stn = starting_stn.copy()
        self.num_reschedules = 0
        self.num_sent_schedules = 0
        # Resample the contingent edges.
        # Super important!
        pr.verbose("Resampling Stored STN")
        self.resample_stored_stn()
        # Create the decoupled substns
        substns = self._instantiate_subproblems(self.stn,
            decouple_type=decouple_type)

        if substns is None:
            pr.verbose("Failed to decouple, falling back to early exec.")

        # Setup options
        first_run = True
        options = [{"first_run": True,
                   "executed_contingent": False,
                   "executed_time": 0.0} for i in range(len(self.stn.agents))]

        # Setup default guide settings
        guides = [self.stn]*len(self.stn.agents)
        current_alpha = 0.0

        # Loop until all timepoints assigned.
        while not self.all_assigned():
            # Update the options so that first_run is only true when it's the
            # actual first run.
            for i in range(len(self.stn.agents)):
                options[i]["first_run"] = first_run

            if first_run:
                first_run = False

            # Calculate the guide STN.
            pr.vverbose("Getting Guide...")
            functiontimer.start("get_guide")
            if substns is not None:
                for i, sub in enumerate(substns):
                    current_alpha, guide_stn = self.get_guide(
                        sub,
                        current_alpha,
                        guides[i],
                        options=options[i])
                    guides[i] = guide_stn
            else:
                for i in range(len(self.stn.agents)):
                    # Use early first as a fallback.
                    guides[i] = self._early_first_guide()
            functiontimer.stop("get_guide")
            pr.vverbose("Got guide")

            # Select the next timepoint.
            pr.vverbose("Selecting timepoint...")
            functiontimer.start("selection")

            # We do this weird new_selection switch so that we select the
            # earliest timepoint from *all* of the guides, not just any one
            # guide.
            # The "selection" variable represents the earliest selection we
            # make, which holds the id, the time, and whether it was
            # contingent.
            selection = None
            for i, guide_stn in enumerate(guides):
                new_selection = self.select_next_timepoint(guide_stn,
                    self._current_time)
                if selection is None:
                    selection = new_selection
                    continue
                if selection[1] > new_selection[1]:
                    selection = new_selection
                options[i]["executed_contingent"] = selection[2]
                options[i]["executed_time"] = selection[1]

            functiontimer.stop("selection")
            pr.vverbose("Selected timepoint, node_id of {}"
                        .format(selection[0]))

            next_vert_id = selection[0]
            next_time = selection[1]
            executed_contingent = selection[2]

            # Propagate constraints (minimise) and check consistency.
            for guide_stn in guides:
                if next_vert_id in guide_stn.verts:
                    self.assign_timepoint(guide_stn, next_vert_id, next_time)
            if substns is not None:
                for i, substn in enumerate(substns):
                    if next_vert_id in substn.verts:
                        #print("For substn {}...".format(i))
                        #print("Assignments: {} to {}".format(next_vert_id,
                        #                                     next_time))
                        self.assign_timepoint(substn, next_vert_id, next_time)
                        #print("After assignment:\n{}".format(substn))
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
            if substns is not None:
                for i, sub in enumerate(substns):
                    sub_copy = sub.copy()
                    subcons = self.propagate_constraints(sub_copy)
                    if subcons:
                        sub = sub_copy
                    else:
                        # The substn is not consistent, but the whole STN is.
                        # This means we do not want to follow the SREA guide
                        # any further. A smart decision here would to now
                        # ignore decoupling constraints, and try to solve the
                        # STN locally. But this is too much effort for this
                        # algorithm. Return failure prematurely instead, and
                        # spit out a warning.
                        pr.warning("Whole STN was consistent, but substn was not.")
                        return False
                pr.vverbose("Done propagating our STN")
                functiontimer.stop("propagation & check")

            #print("Full STN:\n{}".format(self.stn))
            #for i, s in enumerate(substns):
                #print("Substn {}:\n{}".format(i, s))

            # Clean up the STN
            self.remove_old_timepoints(self.stn)
            if substns is not None:
                for sub in substns:
                    self.remove_old_timepoints(sub)

            self._current_time = next_time
        pr.verbose("Assignments: " + str(self.get_assigned_times()))
        assignment_check = self.propagate_constraints(self.assignment_stn)
        if not self.propagate_constraints(self.assignment_stn):
            pr.warning("False positive: assigned all events, but was not a"
                       " solution.")
            return False
        return True

    def assign_timepoint(self, stn, vert_id, time):
        """ Assigns a timepoint to specified time

        Args:
            vert: Node to assign.
            time: float: Time to assign this vert.
        """
        if vert_id != Z_NODE_ID:
            stn.update_edge(
                Z_NODE_ID,
                vert_id,
                time,
                create=True,
                force=True)
            stn.update_edge(
                vert_id,
                Z_NODE_ID,
                -time,
                create=True,
                force=True)
        stn.get_vertex(vert_id).execute()

    def get_guide(self, stn, previous_alpha,
                  previous_guide, options={}) -> tuple:
        """Retrieve a guide STN (dispatch) based on the execution strategy

        Args:
            execution_strat: String representing the execution strategy.
            previous_: The previously used guide STN's alpha.
            previous_guide: The previously used guide STN.
            options (dict, optional): Dictionary of possible options to use for
                the algorithms.

        Returns:
            Returns a tuple with format:
            | [0]: Alpha of the guide.
            | [1]: dispatch (type STN) which the simulator should follow,
        """
        return self._drea_algorithm(stn,
                                    previous_alpha,
                                    previous_guide,
                                    options["first_run"],
                                    options["executed_contingent"])

    def _srea_wrapper(self, stn, previous_alpha, previous_guide):
        """DecoupledSimulator's own SREA Wrapper. Note, we need to pass in the
            STN here.
        """
        self.num_reschedules += 1
        try:
            result = srea.srea(stn)
        except Exception as e:
            #print(e)
            #print("This was the STN that broke SREA:\n"+str(stn))
            srea.srea(stn, debugLP=True)
            #raise AssertionError()
        if result is not None:
            self.num_sent_schedules += 1
            return result[0], result[1]
        # Our guide was inconsistent... um. Well.
        # This is not great.
        # Follow the previous guide?
        return previous_alpha, previous_guide

    def _drea_algorithm(self, stn, previous_alpha, previous_guide, first_run,
                        executed_contingent):
        """ Implements the DREA algorithm. """
        if first_run or executed_contingent:
            ans = self._srea_wrapper(stn, previous_alpha, previous_guide)
            pr.verbose("DREA Rescheduled, new alpha: {}".format(ans[0]))
            return ans
        return previous_alpha, previous_guide

    def _early_first_guide(self):
        return self.stn

    def _instantiate_subproblems(self, stn, decouple_type="opt_inter"):
        """Returns a list of decoupled subproblems"""
        if decouple_type == "opt_inter":
            alpha, subproblems = optdecouple.decouple_agents(stn,
                                                             fidelity=0.005)
        elif decouple_type == "srea":
            alpha, subproblems = sreadecouple.decouple_agents(stn)
        else:
            raise ValueError(("decouple_type {} not"
                              + " found.").format(decouple_type))
        return subproblems

    def remaining_contingent_count(self, stn):
        """Returns the number of remaining (unexecuted) contingent events"""
        # num_cont : Number of remaining unexecuted contingent events
        num_cont = 0
        for i in stn.received_timepoints:
            if not stn.get_vertex(i).is_executed():
                num_cont += 1
        return num_cont
