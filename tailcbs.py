from astar import aStar
from post import post
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
class TailCBS():
    schedule = {}
    finished = False

    def __init__(self, grid, agents, tail):
        self.tail = tail
        self.OPEN = PriorityQueue()
        #Root node setup
        root = cbs_node()
        self.low_level(grid, agents, root)       
        self.SIC(root)
        self.OPEN.put(root, root.cost)

        while not self.OPEN.empty():
            current = self.OPEN.get()
            conflicts = self.validate(current)
            #if goal node
            if self.finished:
                print ("Cost: %d" % current.cost)
                self.schedule = current.solution
                break
            for pos,t in conflicts:
                for (agent,_) in conflicts[pos,t][0]:
                    for (other_agent,_) in conflicts[pos,t][0]:
                        if not other_agent == agent:
                            new_node = cbs_node()            
                                                
                            #Set constraints for the new node
                            new_node.constraints = copy.deepcopy(current.constraints) #dict1 = dict(dict2)
                            # self.addConstraints(new_node, conflicts, pos, t, agent)
                            if conflicts[pos,t][1] == []:
                                self.addConstraints(new_node, conflicts, t, agent, "", current.solution, other_agent)
                            
                            else:
                                for a in conflicts[pos,t][1]:
                                    self.addConstraints(new_node, conflicts, t, agent, a, current.solution, other_agent)

                            print (new_node.constraints)
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

    #constraints: …. … .. .
    def addConstraints(self, node, conflicts, t, agent, a, paths, other_agent):
        #print (conflicts)
                
        if agent in node.constraints:
            for i in range(0, self.tail):
                for j in range(0, i):
                    if t < len(paths[other_agent]):
                        pos = paths[other_agent][t-j]
                        time = t+self.tail-i
                        if pos in node.constraints[agent]:
                            if (time,a) not in node.constraints[agent][pos]:
                                node.constraints[agent][pos].append((time,a))
                        else:
                            node.constraints[agent][pos] = [(time,a)]
                    #else mutherfucker
        else:
            node.constraints[agent] = {}
            node.constraints[agent][paths[agent][t]] = [(t,a)]
            for i in range(0, self.tail):
                for j in range(0, i):
                    if t < len(paths[other_agent]):
                        pos = paths[other_agent][t-j]
                        time = t+self.tail-i
                        if pos in node.constraints[agent]:
                            if (time,a) not in node.constraints[agent][pos]:
                                node.constraints[agent][pos].append((time,a))
                        else:
                            node.constraints[agent][pos] = [(time,a)]
                    #else mutherfucker
    
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
                        self.addConflicts(conflicts, positions,  node, agent, i, i)
                    self.addPos(positions,  node, agent, i, i)

                    #full frontal collisions
                    #If an agents previous position is visited by another and vise versa
                    if node.solution[agent][i-1] in positions:
                        for (a,_) in positions[node.solution[agent][i-1]]:
                            if (node.solution[a][i-1] == node.solution[agent][i]) and not (agent == a):
                                found_conflict = True

                                #Agent1
                                if (node.solution[agent][i],i) in conflicts:
                                    if agent not in conflicts[(node.solution[agent][i],i)]:
                                        conflicts[(node.solution[agent][i],i)][0].append(agent)
                                        conflicts[(node.solution[agent][i],i)][1].append(a)
                                else:
                                    conflicts[(node.solution[agent][i],i)] = ([agent] + positions[node.solution[agent][i]],[a])

                                #Agent2
                                if (node.solution[a][i],i) in conflicts: 
                                    if a not in conflicts[(node.solution[a][i],i)]:
                                        conflicts[(node.solution[a][i],i)][0].append(a)
                                        conflicts[(node.solution[a][i],i)][1].append(agent)

                                else:
                                    conflicts[(node.solution[a][i],i)] = ([a] + positions[node.solution[a][i]],[agent])


                #if the agent is at the goal, we keep checking the goal-position
                else:
                    if node.solution[agent][-1] in positions:
                        found_conflict = True
                        self.addConflicts(conflicts, positions,  node, agent, -1, i )
                    self.addPos(positions,  node, agent, -1, i)

            if found_conflict:
                return conflicts
        if not found_conflict:
            self.finished = True
            return {}

    def addPos(self, positions,  node, agent, i, t):
        if i >= 0:
            for j in range(0,self.tail):
                if node.solution[agent][i-j] in positions:
                    positions[node.solution[agent][i-j]].append((agent, node.solution[agent][i])) 
                else:
                    positions[node.solution[agent][i-j]] = [(agent, node.solution[agent][i])]
        else:
            #if the agent is in the goal we want to make sure the tail gets added to position.
            j = self.tail - (t - len(node.solution[agent]))
            if j >= 0 :
                for k in range(0, j):
                    if node.solution[agent][i-k] in positions:
                        positions[node.solution[agent][i-k]].append((agent, node.solution[agent][i])) 
                    else:
                        positions[node.solution[agent][i-k]] = [(agent, node.solution[agent][i])]



    # i = index for schedule & t = time 
    def addConflicts(self, conflicts, positions,  node, agent, i, t ):
        if (node.solution[agent][i],t) in conflicts:
            conflicts[(node.solution[agent][i],t)][0].append((agent,node.solution[agent][i]))
        else:
            conflicts[(node.solution[agent][i],t)] = ([(agent,node.solution[agent][i])] + positions[node.solution[agent][i]],[])


        #constraints: …. … .. .
