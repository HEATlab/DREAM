import json, sys, os, re
from copy import deepcopy
from math import floor, ceil
import itertools
import argparse
import pulp
from subprocess import Popen,PIPE

from stntools import STN
from stntools.distempirical import invcdf_norm

## \file SREA.py
#
#  \brief Runs the SREA algorithm on an input STN and computes the robustness
#
#  \details To run this file on an STN, use the command:
#  \code{.unparsed}
#  python SREA.py JSONFILE ALPHA
#  \endcode
#
#
#  \note You'll need pulp to be able to run this. On a linux machine run
#  `sudo pip install pulp` or `sudo easy_install -U pulp`.
#  THEN RUN `sudo pulptest`, otherwise it won't work.

## \fn addConstraint(constraint,problem)
#  \brief Adds an LP constraint to the given LP
def addConstraint(constraint,problem):
    problem += constraint
    #print 'adding constraint', constraint

## \fn setUpLP(stn)
#  \brief initializes the LP problem and the LP variables that will not change
#      with alpha
#  \returns A tuple (bounds, deltas, prob) where bounds and deltas are
#      dictionaries of LP variables, and prob is the LP problem instance
def setUpLP(stn, decouple):
    initialBounds = {}
    bounds = {}
    deltas = {}

    prob = pulp.LpProblem('PSTN Robust Execution LP', pulp.LpMaximize)

    # ##
    # Store Original STN edges and objective variables for easy access.
    # Not part of LP yet
    # ##

    for i in stn.verts:
        bounds[(i,'+')] = pulp.LpVariable('t_%d_hi'%i, lowBound = None,
                                                 upBound = stn.get_edge_weight(0,i))

        bounds[(i,'-')] = pulp.LpVariable('t_%d_lo'%i, lowBound = -stn.get_edge_weight(i,0),
                                                 upBound = None)
        addConstraint( bounds[(i,'+')] >= bounds[(i,'-')] , prob)

    for i,j in stn.edges:
        if (i,j) in stn.contingent_edges:
            deltas[(i,j)] = pulp.LpVariable('delta_%d_%d'%(i,j), lowBound = 0, upBound = None)
            deltas[(j,i)] = pulp.LpVariable('delta_%d_%d'%(j,i), lowBound = 0, upBound = None)

        else:
            # ignore edges from z. these edges are implicitly handled with the bounds
            # on the LP variables
            if i != 0 and not decouple:
                addConstraint(bounds[(j,'+')]-bounds[(i,'-')] <= stn.get_edge_weight(i,j),prob)
                addConstraint(bounds[(i,'+')]-bounds[(j,'-')] <= stn.get_edge_weight(j,i),prob)

            elif i != 0 and (i,j) in stn.interagentEdges:
                addConstraint(bounds[(j,'+')]-bounds[(i,'-')] <= stn.get_edge_weight(i,j),prob)
                addConstraint(bounds[(i,'+')]-bounds[(j,'-')] <= stn.get_edge_weight(j,i),prob)


    return (bounds, deltas, prob)


##
# \fn srea(inputstn,debug=False,debugLP=False,lb=0.0,ub=0.999)
# \brief Runs the SREA algorithm on an input STN
#
# @param inputstn The STN that we are running SREA on
# @param invCDF_map A dictionary of dictionaries generated from a
#      distgenlib.invcdf_map call. See documentation there for more info.
# @param debug Print optional status messages about alpha levels
# @param debugLP Print optional status messages about each run of the LP
# @param lb The starting lower bound on alpha for the binary search
# @param ub The starting upper bound on alpha for the binary search
#
# @returns a tuple (alpha, outputstn) if there is a solution, or None if there
#     is no solution
def srea(inputstn,
         debug=False,
         debugLP = False,
         returnAlpha = True,
         decouple = False,
         lb = 0.0,
         ub = 0.999):
    inputstn = inputstn.copy()
    # dictionary of alphas for binary search
    alphas = {i:i/1000.0 for i in range(1001)}

    # bounds for binary search
    lower = ceil(lb * 1000) - 1
    upper = floor(ub * 1000) + 1

    result = None

    # set up LP
    if not decouple:
        # TODO: Change to faster algorithm?
        inputstn.floyd_warshall()
    bounds, deltas, probBase = setUpLP(inputstn, decouple)

    # First run binary search on alpha
    while upper - lower > 1:
        alpha = alphas[(upper + lower) // 2]
        if debug:
            print('trying alpha = {}'.format(alpha))

        # run the LP
        probContainer = (bounds, deltas, probBase.copy())
        LPbounds = srea_LP(inputstn.copy(),
                           alpha,
                           decouple,
                           debug = debugLP,
                           probContainer=probContainer)

        # LP was feasible, try lower alpha
        if LPbounds is not None:
            upper = (upper + lower) // 2
            result = (alpha, LPbounds)
        # LP was infeasable, try higher alpha
        else:
            lower = (upper + lower) // 2

        # finished our search, load the smallest alpha decoupling
        if upper - lower <= 1:
            if result != None:
                alpha, LPbounds = result
                if debug:
                    print('modifying STN with lowest good alpha, {}'.format(alpha))
                for i,sign in LPbounds:
                    if sign == '+':
                        inputstn.update_edge(0, i, ceil(bounds[(i,'+')].varValue))
                    else:
                        inputstn.update_edge(i, 0, ceil(-bounds[(i,'-')].varValue))

                if returnAlpha:
                    return alpha,inputstn
                else:
                    return inputstn
    # skip the rest if there was no decoupling at all
    if result == None:
        if debug:
            print('could not produce feasible LP.')
        return None

    # Fail here
    assert(False)


## \fn srea_LP(inputstn,alpha,debug=False,probContainer=None)
#  \brief Runs the robust execution LP on the input STN at the given alpha
#  level
#
#  @param inputSTN The STN used as an input to the LP
#  @param invCDF_map A dictionary of dictionaries generated from a
#       distgenlib.invcdf_map call. See documentation there for more info.
#  @param alpha The risk level (between 0 and 1) that we are using for the LP
#  @param decouple originally was meant to indicate if we wanted decoupling or not
#   but then we discovered that this already decouples the STN
#  @param debug Print optional status messages
#  @param probContainer Optional tuple of LP variables and the LP problem
#       instance, returned from setUpLP
#
#  \returns A dictionary of the LP_variables for the bounds on timepoints.
def srea_LP(inputstn,
            alpha,
            decouple,
            debug=False,
            probContainer=None
           ):

    # Check some types to make sure everything is the correct type
    if type(inputstn) != STN:
        raise TypeError("inputstn is not of type STN")

    alpha = round(float(alpha),3)
    one_minus_alpha = round(1-float(alpha),3)

    if probContainer is None:
        if debug:
            print('No saved LP variables, generating all LP variables from current STN')
        bounds, deltas, prob = setUpLP(inputstn, decouple)
    else:
        bounds, deltas, prob = probContainer



    for (i,j), edge in list(inputstn.contingent_edges.items()):
        p_ij = invcdf_norm(one_minus_alpha, edge.mu, edge.sigma)
        p_ji = -invcdf_norm(alpha, edge.mu, edge.sigma)
        limit_ij = invcdf_norm(0.997, edge.mu, edge.sigma)
        limit_ji = -invcdf_norm(0.003, edge.mu, edge.sigma)
        #p_ij = 1000*invCDF_map[edge.distribution][one_minus_alpha]
        #p_ji = -1000*invCDF_map[edge.distribution][alpha]
        #limit_ij = 1000*invCDF_map[edge.distribution]['1.0']
        #limit_ji = -1000*invCDF_map[edge.distribution]['0.0']


        deltas[(i,j)].upBound = limit_ij - p_ij
        deltas[(j,i)].upBound = limit_ji - p_ji

        # Lund et al. LP (3)
        addConstraint( bounds[(j,'+')] - bounds[(i,'+')] == p_ij + deltas[(i,j)], prob )
        # Lund et al. LP (4)
        addConstraint( bounds[(j,'-')] - bounds[(i,'-')] == -p_ji - deltas[(j,i)], prob )

    # ##
    # Generate the objective function.
    #   Our objective function is SUM delta_ij
    # ##
    deltaSum = sum( [deltas[(i,j)] for i,j in deltas] )
    prob += deltaSum, 'Maximize time added back to constraints while decoupling'

    if debug:
        prob.writeLP('STN.lp')
        pulp.LpSolverDefault.msg = 10

    ## for RPi only
    # mySolver = solvers.GLPK()
    # prob.solve(solver=mySolver)
    # This try except exists because there was a weird bug with Pulp where
    # it was throwing an error instead of just saying that the lp was not
    # resolvable.  I don't know much about the inner workings of pulp and
    # stack overflow suggested I put in this fix so I did.
    # https://stackoverflow.com/questions/27406858/pulp-solver-error
    try:
        prob.solve()
    except Exception:
        return None

    status = pulp.LpStatus[prob.status]
    if debug:
        print('Status:', status)
        # Each of the variables is printed with it's resolved optimum value
        for v in prob.variables():
            print(v.name, '=', v.varValue)

    if status != 'Optimal':
        return None
    return bounds

## \fn getRobustness(stn)
#  \brief Calls the rust simulator to compute the robustness of the input STN
#  NOTE: This is now depracated
def getRobustness(stn):
    tempstn = 'json/temp.json'

    with open(tempstn, 'w+') as f:
        json.dump(stn.forJSON(), f, indent=2, separators=(',', ':'))

    # Find the robustness of the decoupling
    simulation = Popen(['../stpsimulator/target/release/simulator_stp',
                                  '--samples', str(10000),
                                  '--threads', '4',
                                  '--sample_directory', '../stpsimulator/samples/',
                                  tempstn],
                                  stdout=PIPE, stderr=PIPE)
    simulation.wait()

    dataRegex = re.compile(r'result:\n([0-9\.]+)')

    # extract the robustness from simulator output
    simData = simulation.stdout.read()
    match = dataRegex.search(simData)

    # simulator failed -- 0 robustness
    if match is None:
        return 0

    return float(match.group(1))


## \fn getDispatch(stn)
#  \brief performs srea on the given STN
#
#  \returns STN that represents the dispatch strategy
def getDispatch(stn, invCDF_map):

    output = srea(stn, invCDF_map)

    if output != None:
        alpha,stn = output
        #print getRobustness(stn)
        stn.minimize()
        for (i,j),edge in list(stn.contingent_edges.items()):
            edge_i = stn.getEdge(0,i)
            edge_j = stn.getEdge(0,j)
            edge.Cij = edge_j.getWeightMax()-edge_i.getWeightMax()
            edge.Cji = - (edge_j.getWeightMin()-edge_i.getWeightMin())
            #this loop ensures that the output STN with integer edge weights is still
            #strongly controllable
            for connected_edge in stn.getOutgoing(j):
                edge.Cji = -max(-edge.Cji, edge.Cij-connected_edge.Cji-connected_edge.Cij)
        return stn

    print("srea did not result in a feasible LP, please try again with a different STN")
    return None


## \fn main
#  \brief Sets up and solves the LP
# \deprecated NOTE: This function is now deprecated.
# Do not call srea directly.
def main():
    # handle command line input

    parser = argparse.ArgumentParser()

    parser.add_argument('jsonFile', metavar='JSON', type=str,
            help='STN json file')
    parser.add_argument("-d","--debugAlpha", action = "store_true", dest = "debugAlpha",
            help = "Print alpha level debugging info.")
    parser.add_argument("-D","--debugLP", action = "store_true", dest = "debugLP",
            help = "Print LP debugging info.")
    parser.add_argument("-m", "--makespan", type = int, dest = "makespan",
            help = "Set the makespan for the schedule")
    parser.add_argument("-s","--save", type = str, action = "store",
            dest = "saveSTN",
            help = "Store the output STN in a JSON file.")
    parser.add_argument("-i", "--decouple", action = "store_true", dest = "decoupleLP",
            help = "adds decoupling constraints to LP")

    options = parser.parse_args()

    if options.jsonFile == None:
        parser.error("Incorrect number of arguments")

    try:
        stn = loadSTNfromJSONfile(options.jsonFile)['stn']
    except IOError as e:
        sys.stderr.write("I/O error({0}): {1}\n".format(e.errno, e.strerror))
        print((sys.exc_info()[0]))
        sys.exit(1)
    except TypeError as e:
        sys.stderr.write("Type error: {0}\n".format(e))
        print((traceback.format_exc()))
        sys.exit(1)

    if options.makespan != None:
        stn.setMakespan(options.makespan)
        print("Set makespan to {}".format(options.makespan))

    # FIXME: Do not pass None type to srea's invCDF argument.
    #output = srea(STN, None, debug = options.debugAlpha, debugLP = options.debugLP, decouple = options.decoupleLP)
    raise NotImplementedError

    if output != None:
        alpha,stn = output
        #print getRobustness(stn)
        if not options.debugLP and not options.decoupleLP:
            stn.minimize()
        for (i,j),edge in list(stn.contingent_edges.items()):
            edge_i = stn.getEdge(0,i)
            edge_j = stn.getEdge(0,j)
            edge.Cij = edge_j.getWeightMax()-edge_i.getWeightMax()
            edge.Cji = - (edge_j.getWeightMin()-edge_i.getWeightMin())
            #this loop ensures that the output STN with integer edge weights is still
            #strongly controllable
            for connected_edge in stn.getOutgoing(j):
                edge.Cji = -max(-edge.Cji, edge.Cij-connected_edge.Cji-connected_edge.Cij)
        print(stn)

    if options.saveSTN != None:
        with open(options.saveSTN,"w") as f:
            json.dump(stn.forJSON(), f, indent=2, separators=(',', ':'))

if __name__ == '__main__':
    main()
