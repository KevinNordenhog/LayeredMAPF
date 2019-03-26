from astar import aStar
from CAstar import CAstar
from cbs import CBS

class GlobalPlanner:
    schedule = {}
    planner = "Planner not chosen"
    def __init__(self, grid, agents):
        if len(agents) == 1:
            self.planner = "AStar"
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal, self.constraints)
        else:
            #self.planner = "CAstar"
            #alg = CAstar(grid, agents)
            self.planner = "CBS"
            alg = CBS(grid, agents)
            self.schedule = alg.schedule
        #print (self.schedule)
