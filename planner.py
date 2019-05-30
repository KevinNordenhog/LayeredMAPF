from astar import aStar
from CAstar import CAstar
from cbs import CBS
from ecbs import ECBS
from tailcbs import TailCBS
from Optimizedtailcbs import OptTailCBS
from post import post
from component import getComponent
from component import getBoundedComponent
import sys
import time
from copy import deepcopy

class Planner:
    schedule = {}
    cost = 0
    makespan = 0
    planner = "Planner not chosen"
    delay_tolerance = sys.maxsize
    stalling = False
    #stalling = False
    stalling_bound = 0
    comp_schedule = {}

    # Evaluation data
    time_global = 0
    time_local = []
    init_schedule = {}
    deviation_count = 0
    tot_deviations = 0
    no_stalls = 0
    no_recalc = 0
    local = False
    tot_makespan = 0
    tot_sic = 0

    def __init__(self, grid, agents, alg, tolerance):
        self.planner = alg
        self.delay_tolerance = tolerance
        time_start = time.time()
        self.globalPlanner(grid, agents)
        self.init_schedule = deepcopy(self.schedule)
        self.time_global = time.time()-time_start
        self.evaluate(grid, agents, {})


    # Find a MAPF plan for the given grid, agents, and algorithm
    def globalPlanner(self, grid, agents):
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
            self.cost = sic(self.schedule)
            self.makespan = makespan(self.schedule)
            if self.planner == "tailcbs":
                self.delay_tolerance = post(self.schedule)
            else:
                self.delay_tolerance = 0

            # Reset parameters when stalling
            if self.stalling:
                for agent in self.schedule:
                    agents[agent].stall = 0
                    agents[agent].delay = 0
                    agents[agent].iswaiting = False
                    
        return self.schedule
    
    # Based on the deviations that occured, the exisiting schedule,
    # and the current state of the map, find a new plan
    def localplanner(self, deviations, grid, agents):
        # If the map has changed, 
        #if dynamic: TODO:
        #    self.globalPlanner(grid, agents)
        #    return
        # Check if delay is small enough to skip recomputation
        for agent in agents:
            self.comp_schedule[agent] = [agents[agent].pos] + self.schedule[agent]

        self.local = True
        addStall = False
        recompute = False
        self.tot_deviations += len(deviations)
        self.deviation_count += 1
        stalled_agents = []
        for agent in deviations:
            if agents[agent].delay > self.delay_tolerance:
                if self.stalling:
                    addStall = True
                    self.stallComponent(deviations, agents, stalled_agents, agent)
                    for a in agents:
                        if agents[a].stall > self.stalling_bound and not self.stalling_bound == 0:
                            recompute = True 
                else:
                    recompute = True
                if recompute:
                    time_start = time.time()
                    self.globalPlanner(grid, agents)
                    time_planner = time.time()-time_start
                    self.time_local += [time_planner]
                    self.no_recalc += 1
                    return True
        if not recompute:
            if addStall:
                self.no_stalls += 1
            return False

    def stallComponent(self, deviations, agents, stalled_agents, agent):
        if self.stalling and not deviations == []:
            if agent in stalled_agents:
                return
            tmp = self.schedule[agent].pop(0) # Temporally remove next pos
            agents[agent].stall += 1 
            if self.stalling_bound > 0:
                comp = getBoundedComponent(self.comp_schedule, agent, 0, self.stalling_bound)
            else:
                comp = getComponent(self.comp_schedule, agent, 0)            
            for a in comp:
                #We do not want to stall any agents more than once
                if not a in stalled_agents and not a in deviations:
                    agents[a].stall += 1
                    self.schedule[a].insert(0, agents[a].pos)
                    stalled_agents.append(a)
            self.schedule[agent].insert(0, tmp)

    
    # Evaluate the execution
    # (Local planner is only evaluated if executed)
    def evaluate(self, grid, agents, paths):
        # Global planner evaluation
        print ("----------------------------------")
        print ("Evaluation (global planner):")
        print ("----------------------------------")
        print ("Planner: %s" % self.planner)
        print ("Execution time: %f" % (self.time_global))
        print ("Number of agents: %d" % len(agents))
        print ("Size of grid: %dx%d" % (grid.width, grid.heigth))
        print ("Makespan: %d" % makespan(self.init_schedule))
        print ("Sum of individual cost: %d" % sic(self.init_schedule))
        print ("Delay tolerance: %d" % (post(self.init_schedule)))
        print ("----------------------------------")
        # Local planner evaluation
        if self.local:
            #self.tot_makespan = 0
            self.tot_sic = 0
            self.tot_makespan = makespan(paths) + 1
            for name, agent in agents.items():
                self.tot_sic += len(paths[agent.name])
            print ("\n----------------------------------")
            print ("Evaluation (local planner):")
            print ("----------------------------------")
            print ("Planner: ?")
            print ("Total excution time: %f" % sum(self.time_local))
            print ("Number of deviations: %d" % self.deviation_count)
            print ("Total number of deviation: %d" % self.tot_deviations)
            print ("Local planner executions: %d" % len(self.time_local))
            print ("Total makespan: %d" % self.tot_makespan)
            print ("Total sum of individual cost: %d" % self.tot_sic)
            print ("Number of stalls: %d" % self.no_stalls)
            print ("Number of recalculations: %d" % self.no_recalc)
            print ("----------------------------------")
        else:
            self.tot_sic = sic(self.init_schedule)
            self.tot_makespan = makespan(self.init_schedule)
    

# Put the values in the dictionary into a list
def dict2list(dictionary):
    dictlist = []
    for key, value in dictionary.items():
        dictlist.append(value)
    return dictlist

# The length of the longest path in schedule
def makespan(schedule):
    if schedule:
        return len(max(schedule.values(), key=lambda s: len(s)))-1
    else:
        return -1

#Sum of individual cost
def sic(schedule):
    s = 0
    for agent in schedule:    
        s += len(schedule[agent])-1
    return s
