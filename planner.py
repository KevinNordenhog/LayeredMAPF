from astar import aStar
from CAstar import CAstar
from cbs import CBS
from ecbs import ECBS
from tailcbs import TailCBS
from Optimizedtailcbs import OptTailCBS
from post import post
import sys
import time
from copy import deepcopy

class Planner:
    schedule = {}
    planner = "Planner not chosen"
    delay_tolerance = sys.maxsize

    # Evaluation data
    time_global = 0
    time_local = []
    init_schedule = {}
    deviation_count = 0
    delay_tolerance = 2

    def __init__(self, grid, agents, alg):
        self.planner = alg
        time_start = time.time()
        self.globalPlanner(grid, agents)
        self.init_schedule = deepcopy(self.schedule)
        self.time_global = time.time()-time_start
        self.evaluate(grid, agents)


    # Find a MAPF plan for the given grid, agents, and algorithm
    def globalPlanner(self, grid, agents):
        print ("Path finding algorithm is running.")
        agent_list = dict2list(agents)
        # Run algorithn according to input
        if len(agent_list) == 1:
            self.planner = "AStar"
            self.schedule[agent_list[0].name] = aStar(grid.grid,
                    agent_list[0].pos, agent_list[0].goal, {})
        else:
            if self.planner == "castar":
                alg = CAstar(grid.grid, agent_list)
            elif self.planner == "cbs":
                alg = CBS(grid.grid, agent_list, agents)
                self.node_cnt = alg.OPEN.i
            elif self.planner == "ecbs":
                alg = ECBS(grid.grid, agent_list)
            elif self.planner == "tailcbs":
                alg = TailCBS(grid.grid, agent_list, self.delay_tolerance, agents)
                self.node_cnt = alg.OPEN.i
            elif self.planner == "otailcbs":
                alg = OptTailCBS(grid.grid, agent_list, self.delay_tolerance, agents)
                self.node_cnt = alg.OPEN.i
            self.schedule = alg.schedule
            self.delay_tolerance = post(self.schedule)
            print ("New delay tolerance is %d." % self.delay_tolerance)
        return self.schedule
    
    # Based on the deviations that occured, the exisiting schedule,
    # and the current state of the map, find a new plan
    def localplanner(self, deviations, grid, agents):
        # If the map has changed, 
        if dynamic:
            self.globalPlanner(grid, agents)
            return
        # Check if delay is small enough to skip recomputation
        recompute = False
        self.deviation_count += len(deviations)
        for agent in deviations:
            if agents[agent].delay > self.delay_tolerance:
                time_start = time.time()
                self.globalPlanner(grid, agents)
                time_planner = time.time()-time_start
                self.time_local += [time_planner]
                recompute = True
                break
        if not recompute:
            print ("The delay can be tolerated.")
    
    # Evaluate the execution
    # (Local planner is only evaluated if executed)
    def evaluate(self, grid, agents):
        # Global planner evaluation
        print ("\n----------------------------------")
        print ("Evaluation (global planner):")
        print ("----------------------------------")
        print ("Planner: %s" % self.planner)
        print ("Execution time: %f" % (self.time_global))
        print ("Number of agents: %d" % len(agents))
        print ("Size of grid: %dx%d" % (grid.width, grid.heigth))
        print ("Makespan: %d" % makespan(self.init_schedule))
        print ("Delay tolerance: %d" % (post(self.init_schedule)))
        print ("----------------------------------")
        # Local planner evaluation
        if self.time_local:
            print ("\n----------------------------------")
            print ("Evaluation (local planner):")
            print ("----------------------------------")
            print ("Planner: delay tolerance")
            print ("Total excution time: %f" % sum(self.time_local))
            print ("Number of deviations: %d" % self.deviation_count)
            print ("Local planner executions: %d" % len(self.time_local))
            print ("----------------------------------")
            
    

# Put the values in the dictionary into a list
def dict2list(dictionary):
    dictlist = []
    for key, value in dictionary.items():
        dictlist.append(value)
    return dictlist

# The length of the longest path in schedule
def makespan(schedule):
    if schedule:
        return len(max(schedule.values(), key=lambda s: len(s)))
    else:
        return -1
