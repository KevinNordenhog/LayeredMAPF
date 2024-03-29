from astar import aStar
from post import post
import heapq
import copy
import time

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
            

# Conflict based search
class TailCBS():
    schedule = {}
    finished = False

    def __init__(self, grid, agents, tail, agent_dict):
        self.tail = tail
        self.OPEN = PriorityQueue()
        self.const = []
        #Root node setup
        root = cbs_node()

        #Run the low level for all agents
        for agent in agents:
            self.low_level(grid, agent, root)

        self.SIC(root)
        self.OPEN.put(root, root.cost)

        while not self.OPEN.empty():
            current = self.OPEN.get()
            conflicts = self.validate(current)
            if not conflicts:  # Goal reached
                self.schedule = current.solution
                break
            # Set constraints for the new node
            for pos, c_agents in conflicts.items():
                # Expand each conflicting node
                for i in range(0, len(c_agents)):
                    new_node = cbs_node()            
                    new_node.valid = True
                    # Add constraints to new node
                    new_node.constraints = copy.deepcopy(current.constraints)
                    for j in range(0, len(c_agents)):
                        if i == j:
                            continue
                        agent = c_agents[i][0]
                        t1 = c_agents[i][1]
                        other_agent = c_agents[j][0]
                        t2 = c_agents[j][1]
                        self.addConstraints(new_node, current.solution, 
                                agent, t1, other_agent, t2)
                    if new_node.constraints in self.const: 
                        continue
                    self.const.append(new_node.constraints)
                    if not new_node.valid:
                        continue
                    
                    new_node.solution = copy.copy(current.solution)

                    # Find solution taking constraints into account
                    self.low_level(grid, agent_dict[agent], new_node)                 
                    valid = True
                    for agent in new_node.solution:
                        if not new_node.solution[agent]:
                            valid = False
                    # Only expand nodes containning path for all agents
                    if valid:
                        self.SIC(new_node) # sum of individual cost of node
                        self.OPEN.put(new_node, new_node.cost) 

    # For a given agent and conflict, add a constraint at the position of
    # conflict that says that the conflicting agent may not step there for as long as
    # the tail remains
    def addConstraints(self, node, paths, agent, t1, other_agent, t2):
        #print("t/agent/other_agent", t2, agent, other_agent)
        if t1==0:
            node.valid = False
        if not agent in node.constraints:
            node.constraints[agent] = {}
        tmp = t2 if t2<len(paths[other_agent]) else -1
        pos = paths[other_agent][tmp]
        for i in range(-self.tail, self.tail+1):
            if t2+i <= 0:
                continue
            if not pos in node.constraints[agent]:
                node.constraints[agent][pos] = []
            # Add contraints (and make sure contraints doesn't exist already)
            if not t2+i in [time for time,_ in node.constraints[agent][pos]]:
                node.constraints[agent][pos].append((t2+i, ""))
                #print("%s: (%s, t=%d) cause %s" % (agent, pos, t2+i,other_agent))
   
    # Find a new solution that satisfies the given constraints (astar)
    def low_level(self, grid, agent, node):
        if agent.name in node.constraints:
            node.solution[agent.name] = aStar(grid, agent.pos, agent.goal, node.constraints[agent.name])
        else:
            node.solution[agent.name] = aStar(grid, agent.pos, agent.goal, {})

    #Sum of individual cost (sum of all individual path lengths)
    def SIC(self, node):
        s = 0
        for agent in node.solution:    
            s += len(node.solution[agent])
        node.cost = s

    # The length of the longest path in schedule
    def makespan(self, solution):
        return len(solution[max(solution, key = lambda x: len(solution[x]))])
       
    # Check if a solution is valid or not
    # (No collisions, and delay tolerance should be satisfied)
    def validate(self, node):
        conflicts = {}
        longest_path = self.makespan(node.solution)
        for t in range(0, longest_path):
            positions = {}
            # The position of each agent and their tails at time t
            for agent in node.solution:
                self.addPos(positions, node, agent, t)
            # Validate that the path of each agent does not conflict with other
            # agents at time t.
            for pos, agents in positions.items():
                if len(agents) > 1:
                    conflicts[pos] = agents
                    return conflicts
        # Optimal solution found if there is no conflict
        return conflicts

    # Set the current position of an agent and its tail
    def addPos(self, positions,  node, agent, t):
        for k in range(0, self.tail+1):
            time = t-k
            pos = t-k
            if time < 0: # Check for negative time
                continue
            if time >= len(node.solution[agent]):
                time = t
                pos = len(node.solution[agent])-1
            if node.solution[agent][pos] in positions:
                c = [x for x,_ in positions[node.solution[agent][pos]]] # agent
                n = [x for _,x in positions[node.solution[agent][pos]]] # time
                # Update the time of the agent if it is in list already
                # (only save the latest time on that position)
                if agent in c: #
                    i = c.index(agent)
                    if time > n[i]:
                        positions[node.solution[agent][pos]][i][1] = time
                # If agent is not in list, add it
                else:
                    positions[node.solution[agent][pos]].append((agent, time))
            else:
                positions[node.solution[agent][pos]] = [(agent, time)]
            

    # Add a conflict on position pos at time t 
    def addConflicts(self, node, t, conflicts, agent, positions):
        pos_cnt = t if t < len(node.solution[agent]) else -1
        pos = node.solution[agent][pos_cnt]
        if (pos,t) in conflicts:
            conflicts[(pos,t)][0].append((agent,pos))
        else:
            conflicts[(pos,t)] = ([(agent, pos)] + positions[pos], [])

