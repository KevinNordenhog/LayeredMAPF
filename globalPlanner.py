from astar import aStar

class GlobalPlanner:
    schedule = {}
    def __init__(self, grid, agents):
        print (agents)
        if len(agents) == 1:
            #start = grid[agents[0].x][agents[0].y]
            #goal = grid[agents[0].goal[0]][agents[0].goal[1]]
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal)
        else:
            for agent in agents:
                #self.schedule[agent.name] = list(reversed(aStar(grid, agent.pos, agent.goal)))
                self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal)[::-1]

        print (self.schedule)
