from astar import aStar
from CAstar import CAstar
from cbs import CBS
from ecbs import ECBS
from post import post

class GlobalPlanner:
    schedule = {}
    planner = "Planner not chosen"
    def __init__(self, grid, agents, alg):
        if len(agents) == 1:
            self.planner = "AStar"
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal, {})
        else:
            if alg=="castar":
                self.planner = "CAstar"
                alg = CAstar(grid, agents)
            elif alg=="cbs":
                self.planner = "CBS"
                alg = CBS(grid, agents)
            elif alg=="ecbs":
                self.planner = "ECBS"
                alg = ECBS(grid, agents)
            self.schedule = alg.schedule
            self.window = post(self.schedule)
            print (self.window)
        #print (self.schedule)
