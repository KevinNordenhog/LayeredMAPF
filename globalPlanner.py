from astar import aStar
from CAstar import CAstar

class GlobalPlanner:
    schedule = {}
    def __init__(self, grid, agents):
        if len(agents) == 1:
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal, self.constraints)
        else:
            alg = CAstar(grid, agents)
            self.schedule = alg.schedule
        #print (self.schedule)
