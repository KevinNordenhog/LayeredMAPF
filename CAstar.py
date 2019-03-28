from astar import aStar

#Cooperative A*
class CAstar():

    constraints = {}
    schedule = {}

    def __init__(self, grid, agents):
        self.constraints = {}
        for agent in agents:
            self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal, self.constraints)
            i = 0
            for position in self.schedule[agent.name]:
                if position == self.schedule[agent.name][-1]:
                    if position in self.constraints:
                        self.constraints[position].append((-i, agent))
                    else:
                        self.constraints[position] = [(-i, agent)]
                else:
                    if position in self.constraints:
                        self.constraints[position].append((i,agent))
                    else:
                        self.constraints[position] = [(i,agent)]
                i += 1
