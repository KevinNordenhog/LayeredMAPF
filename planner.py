from astar import aStar
from CAstar import CAstar
from cbs import CBS
from ecbs import ECBS
from post import post
import sys
import time

class Planner:
    schedule = {}
    planner = "Planner not chosen"
    delay_tolerance = sys.maxsize

    def __init__(self, grid, agents, alg):
        self.planner = alg
        self.globalPlanner(grid, agents)


    # Find a MAPF plan for the given grid, agents, and algorithm
    def globalPlanner(self, grid, agents):
        agent_list = dict2list(agents)
        # Run algorithn according to input
        if len(agent_list) == 1:
            self.planner = "AStar"
            self.schedule[agents[0].name] = aStar(grid.grid, agents[0].pos, agents[0].goal, {})
        else:
            if self.planner =="castar":
                alg = CAstar(grid.grid, agent_list)
            elif self.planner =="cbs":
                alg = CBS(grid.grid, agent_list)
            elif self.planner =="ecbs":
                alg = ECBS(grid, agent_list)
            self.schedule = alg.schedule
            self.delay_tolerance = post(self.schedule)
        return self.schedule
    
    # Based on the deviations that occured,
    # and the current state of the map, find a new plan
    def localplanner(self, deviations, grid, agents):
        print ("Local planner executing")
        start = time.time()
        recompute = False
        for agent in deviations:
            if agents[agent].delay > self.delay_tolerance:
                print ("Local planner recomputing path due to %s:" % agent)
                self.globalPlanner(grid, agents)
                end = time.time()
                self.evaluate(start, end, grid, agents)
                recompute = True
                break
        if not recompute:
            print ("The delay can be tolerated. Recalculation not needed")
    
    # Evaluate the latest execution of the planner
    # Print info about the problem and the schedule
    def evaluate(self, start, end, grid, agents):
        # Evaluate execution 
        print ("----------------------------------")
        print ("Planner: %s" % self.planner)
        print ("Execution time: %f" % (end-start))
        print ("Number of agents: %d" % len(agents))
        print ("Size of grid: %dx%d" % (grid.width, grid.heigth))
        success_cnt = 0
        for agent in agents:
            if self.schedule[agent]:
                success_cnt += 1
        completion = 100*(success_cnt/len(agents))
        print ("Completion rate: %d%%" % completion)
        print ("Makespan: %d" % (len(max(self.schedule.values(), key=lambda
                schedule: len(schedule)))))
        print ("Delay tolerance: %d" % (post(self.schedule)))
        print ("----------------------------------")


def dict2list(dictionary):
    dictlist = []
    for key, value in dictionary.items():
        dictlist.append(value)
    return dictlist
