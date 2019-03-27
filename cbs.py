from astar import aStar
import heapq
import copy

class PriorityQueue:
    #used to pick objects with the same priority 
    #without this heappop tries to compare objects (obj1 < obj2), which does not work
    i = 0
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, self.i, item))
        self.i += 1
    
    def get(self):
        #print (self.elements)
        return heapq.heappop(self.elements)[2]

class cbs_node:
    constraints = {}
    solution = {}
    cost = 0
        
    def __init__(self):
        pass
    
    #for suboptimal cbs
    def get_size(self):
        size = 0
        for agent in self.constraints:
            for pos in self.constraints[agent]:
                size += len(self.constraints[agent][pos])
        return size
            

#Conflict based search
class CBS():
    schedule = {}
    finished = False

    def __init__(self, grid, agents):
        self.OPEN = PriorityQueue()
        #Root node setup
        root = cbs_node()
        self.low_level(grid, agents, root)       
        self.SIC(root)
        self.OPEN.put(root, root.cost)

        while not self.OPEN.empty():
            current = self.OPEN.get()
            print (current.constraints)
            print (current.cost)
            conflicts = self.validate(current)
            #if goal node
            if self.finished:
                print ("Cost: %d" % current.cost)
                self.schedule = current.solution
                break
            for pos,t in conflicts:
                for agent in conflicts[pos,t]:
                    new_node = cbs_node()            
                                        
                    #Set constraints for the new node
                    new_node.constraints = copy.deepcopy(current.constraints) #dict1 = dict(dict2)

                    if agent in new_node.constraints:
                        if pos in new_node.constraints[agent]:
                            if t not in new_node.constraints[agent][pos]:
                                new_node.constraints[agent][pos].append(t)
                        else:
                            new_node.constraints[agent][pos] = [t]
                    else:
                        new_node.constraints[agent] = {}
                        new_node.constraints[agent][pos] = [t]
                    

                    #Find solution
                    self.low_level(grid, agents, new_node)                  
                    valid = True
                    for agent in new_node.solution:
                        if new_node.solution[agent] == []:
                            valid = False
                    
                    #Only expand nodes containning path for all agents
                    if valid:
                        #Find cost for the node
                        self.SIC(new_node)
                        self.OPEN.put(new_node, new_node.cost)           

    def low_level(self, grid, agents, node):
        paths = {}
        for agent in agents:
            if agent.name in node.constraints:
                paths[agent.name] = aStar(grid, agent.pos, agent.goal, node.constraints[agent.name])
            else:
                paths[agent.name] = aStar(grid, agent.pos, agent.goal, {})
        node.solution = paths

    #Sum of individual cost
    def SIC(self, node):
        s = 0
        for agent in node.solution:    
            s += len(node.solution[agent])
        node.cost = s
       
    def validate(self, node):
        conflicts = {}
        found_conflict = False
        #loops from i=0 to i=length of the longest path
        for i in range(0, len(node.solution[max(node.solution, key = lambda x: len(node.solution[x]))])):
            positions = {}
            for agent in node.solution:
                if i < len(node.solution[agent]):
                    if node.solution[agent][i] in positions:
                        found_conflict = True
                        if (node.solution[agent][i],i) in conflicts:
                            conflicts[(node.solution[agent][i],i)].append(agent)
                        else:
                            conflicts[(node.solution[agent][i],i)] = [agent] + positions[node.solution[agent][i]]
                        
                        positions[node.solution[agent][i]].append(agent) 
                    else:
                        positions[node.solution[agent][i]] = [agent]
                    #full frontal collisions
                    #If an agents previous position is visited by another and vise versa
                    if node.solution[agent][i-1] in positions:
                        for a in positions[node.solution[agent][i-1]]:
                            if (node.solution[a][i-1] == node.solution[agent][i]) and not (agent == a):
                                found_conflict = True

                                #Agent1
                                if (node.solution[agent][i],i) in conflicts:
                                    if agent not in conflicts[(node.solution[agent][i],i)]:
                                        conflicts[(node.solution[agent][i],i)].append(agent)
                                else:
                                    conflicts[(node.solution[agent][i],i)] = [agent] + positions[node.solution[agent][i]]

                                #Agent2
                                if (node.solution[a][i],i) in conflicts: 
                                    if a not in conflicts[(node.solution[a][i],i)]:
                                        conflicts[(node.solution[a][i],i)].append(a)
                                else:
                                    conflicts[(node.solution[a][i],i)] = [a] + positions[node.solution[a][i]]


                #if the agent is at the goal, we keep checking the goal-position
                else:
                    #print (positions)
                    #print (node.solution[agent])
                    if node.solution[agent][-1] in positions:
                        found_conflict = True
                        if (node.solution[agent][-1],i) in conflicts:
                            conflicts[(node.solution[agent][-1],i)].append(agent)
                        else:
                            conflicts[(node.solution[agent][-1],i)] = [agent] + positions[node.solution[agent][-1]]

                        positions[node.solution[agent][-1]].append(agent)
                    else:
                        positions[node.solution[agent][-1]] = [agent]

            if found_conflict:
                return conflicts
        if not found_conflict:
            self.finished = True
            return {}

