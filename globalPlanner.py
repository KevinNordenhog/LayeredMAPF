from astar import aStar

class GlobalPlanner:
    schedule = {}
    def __init__(self, grid, agents):
        if len(agents) == 1:
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal)
        else:
            for agent in agents:
                self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal)[::-1]
