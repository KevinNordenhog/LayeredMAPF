import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        #print (self.elements)
        return heapq.heappop(self.elements)[1]

# [objects], (x,y), (x,y), {(x,y): [t1,t2,t3]}
def aStar(grid, start, goal, constraints):
    if start == goal:
        return [goal]
    frontier = PriorityQueue()
    frontier.put(start + (0,), 0)
    came_from = {}
    cost_so_far = {}
    time = {}
    came_from[(start + (0,))] = None
    cost_so_far[(start + (0,))] = 0
    time[start + (0,)] = 0 
    path = []

    done = False
    
    if goal in constraints:
        min_finish_time = max(constraints[goal])[0]
    else:
        min_finish_time = 0

    while not frontier.empty():
        current = frontier.get()
        if ((current[0],current[1]) == goal and cost_so_far != 0
                and min_finish_time < cost_so_far[current]):
            done = True
            break
        # Add neighbours to priority queue
        temp = (current[0], current[1], current[2]+1)
        for node in neighbours(grid, current) + [temp]: 
            new_cost = cost_so_far[current] + 1
            new_time = time[current] + 1 
            roof = findRoof(constraints)
            # If there already is a better path to this neighbour, let it be 
            if not ((node not in cost_so_far or new_cost < cost_so_far[node]) 
                    and node[2] <= roof):
                continue
            # Dont check neighbours with constraints
            if (node[0],node[1]) in constraints:
                skip = False
                for t in constraints[(node[0], node[1])]: 
                    if t[0] < 0 and abs(t[0]) <= new_time:
                        skip = True
                    if t[0] == new_time:
                        skip = True
                if skip: 
                    continue

            # Dont swap positions with neighbours
            if ((node[0],node[1]) in constraints
                    and (current[0],current[1]) in constraints):
                node_history = constraints[(node[0],node[1])]
                current_history = constraints[(current[0], current[1])]
                agent_node, agent_current = "node", "current"
                for (t, agent) in node_history:
                    if time[current] == abs(t) and not agent == "":
                       agent_node = agent
                for (t, agent) in current_history:
                    if new_time == abs(t) and not agent == "":
                        agent_current = agent
                if agent_node == agent_current and not agent_node == "":
                    continue

            cost_so_far[node] = new_cost
            time[node] = new_time
            prio = new_cost + heuristic(goal, node[:2])
            frontier.put(node, prio)
            came_from[node] = current
    if done:
        temp = current
        while (temp in came_from):
            path.append((temp[0],temp[1]))
            temp = came_from[temp]

    return path[::-1]



def neighbours(grid, node):
    neigh = []
    width = len(grid) # 21
    heigth = len(grid[0]) # 20
    if ((0 <= (node[0]+1) < width) and (0 <= (node[1]) < heigth)):
        if not grid[node[0]+1][node[1]].obstacle:
            neigh.append(((node[0]+1),(node[1]), node[2]))
    if ((0 <= (node[0]-1) < width) and (0 <= (node[1]) < heigth)):
        if not grid[node[0]-1][node[1]].obstacle:
            neigh.append(((node[0]-1),(node[1]), node[2]))
    if ((0 <= (node[0]) < width) and (0 <= (node[1]+1) < heigth)):
        if  not grid[node[0]][node[1]+1].obstacle:
            neigh.append(((node[0]),(node[1]+1), node[2]))
    if ((0 <= (node[0]) < width) and (0 <= (node[1]-1) < heigth)):
        if not grid[node[0]][node[1]-1].obstacle:
            neigh.append(((node[0]),(node[1]-1), node[2]))
    return neigh

#calculated an estimated distance to the goal
def heuristic(goal, node):
    (x1, y1) = goal
    (x2, y2) = node
    return abs(x1-x2) + abs(y1-y2)


def findRoof(constraints):
    roof = 1

    for i in constraints.values():
        if max(i)[0] > roof:
            roof = max(i)[0]
    return roof
