from astar import aStar

class GlobalPlanner:
    schedule = {}
    constraints = {(2,3): [5], (2,5): [3], (3,6): [3], (3,7): [4]}
    def __init__(self, grid, agents):
        if len(agents) == 1:
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal, self.constraints)[::-1]
        else:
            for agent in agents:
                self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal, self.constraints)[::-1]

        #print (self.schedule)
