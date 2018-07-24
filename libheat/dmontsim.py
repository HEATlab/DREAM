import numpy as np


from .montsim import Simulator
from . import optdecouple
from . import srea
from . import functiontimer
from . import printers as pr


Z_NODE_ID = 0


class DecoupledSimulator(Simulator):

    def simulate(self, starting_stn, sim_options={}):
        ''' Run one simulation.

        Args:
            starting_stn: The STN used to run in the simulation.

        Keyword Args:
            sim_options: A dictionary of possible options to pass into the

        Returns:
            Boolean indicating whether the simulation was successful or not.
        '''
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
        substns = self._instantiate_subproblems(self.stn)

        # Setup options
        first_run = True
        options = [{"first_run": True,
                   "executed_contingent": False,
                   "executed_time": 0.0} for i in range(len(substns))]

        # Setup default guide settings
        guides = [self.stn]*len(self.stn.agents)
        current_alpha = 0.0

        # Loop until all timepoints assigned.
        while not self.all_assigned():
            # Update the options so that first_run is only true when it's the
            # actual first run.
            for i in range(len(substns)):
                options[i]["first_run"] = first_run

            if first_run:
                first_run = False

            # Calculate the guide STN.
            pr.vverbose("Getting Guide...")
            functiontimer.start("get_guide")
            for i, sub in enumerate(substns):
                current_alpha, guide_stn = self.get_guide(sub,
                                                          current_alpha,
                                                          guides[i],
                                                          options=options[i])
                guides[i] = guide_stn
            functiontimer.stop("get_guide")
            pr.vverbose("Got guide")

            # Select the next timepoint.
            pr.vverbose("Selecting timepoint...")
            functiontimer.start("selection")
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
            for substn in substns:
                if next_vert_id in substn.verts:
                    self.assign_timepoint(substn, next_vert_id, next_time)
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
        assignment_check = self.propagate_constraints(self.assignment_stn)
        assert (self.propagate_constraints(self.assignment_stn))
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
        """ Retrieve a guide STN (dispatch) based on the execution strategy
        Args:
            execution_strat: String representing the execution strategy.
            previous_: The previously used guide STN's alpha.
            previous_guide: The previously used guide STN.
            options (dict, optional): Dictionary of possible options to use for
                the algorithms.

        Returns:
            Returns a tuple with format:
            [0]: Alpha of the guide.
            [1]: dispatch (type STN) which the simulator should follow,
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
        result = srea.srea(stn)
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

    def _instantiate_subproblems(self, stn):
        """Returns a list of decoupled subproblems"""
        alpha, subproblems = optdecouple.decouple_agents(stn, fidelity=0.005)
        return subproblems

    def remaining_contingent_count(self, stn):
        """Returns the number of remaining (unexecuted) contingent events"""
        # num_cont : Number of remaining unexecuted contingent events
        num_cont = 0
        for i in stn.received_timepoints:
            if not stn.get_vertex(i).is_executed():
                num_cont += 1
        return num_cont
