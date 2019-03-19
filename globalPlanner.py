from astar import aStar

class GlobalPlanner:
    schedule = {}
    constraints = {(2,3): [5], (2,5): [3], (3,6): [3], (3,7): [4]}
    def __init__(self, grid, agents):
        if len(agents) == 1:
            self.schedule[agents[0].name] = aStar(grid, agents[0].pos, agents[0].goal, self.constraints)#[::-1]
        else:
            self.CAstar(grid, agents)
            # for agent in agents:
            #     self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal, self.constraints)#[::-1]

        print (self.schedule)

    #Cooperative A*
    def CAstar(self, grid, agents):
        for agent in agents:
            self.schedule[agent.name] = aStar(grid, agent.pos, agent.goal, self.constraints)
            i = 0
            for position in self.schedule[agent.name]:
                if position in self.constraints:
                    self.constraints[position].append(i)
                else:
                    self.constraints[position] = [i]
                i += 1


        print (self.constraints)