import astar
from astar import aStar

class GlobalPlanner:
    def __init__(self, grid, agents):
        #print (grid)
        if len(agents) == 1:
            #start = grid[agents[0].x][agents[0].y]
            #goal = grid[agents[0].goal[0]][agents[0].goal[1]]
            self.schedule = aStar(grid, agents[0].pos, agents[0].goal)
    
    
