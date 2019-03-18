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
    frontier = PriorityQueue()
    frontier.put(start + (0,), 0)
    came_from = {}
    cost_so_far = {}
    time = {}
    came_from[(start + (0,))] = None
    cost_so_far[(start + (0,))] = 0
    time[start + (0,)] = 0 
    path = []

    #print (constraints)
    done = False

    while not frontier.empty():
        current = frontier.get()
        if (current[0],current[1]) == goal:
            done = True
            break
 
        temp = (current[0], current[1], current[2]+1)
        for node in neighbours(grid, current) + [temp]: 
            new_cost = cost_so_far[current] + 1
            new_time = time[current] + 1 
            
            if ((node not in cost_so_far) or new_cost < cost_so_far[node]) and node[2] < 50: 
                if (node[0],node[1]) in constraints:
                    if new_time in constraints[(node[0],node[1])]:
                        # print ("RIP")
                        # print (new_time)
                        # print (node)
                        # print (constraints)
                        break
                cost_so_far[node] = new_cost
                time[node] = new_time
                prio = new_cost + heuristic(goal + (0,), node)
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
    if ((0 <= (node[0]+1) < len(grid)) and (0 <= (node[1]) < len(grid))):
        if not grid[node[0]+1][node[1]].obstacle:
            neigh.append(((node[0]+1),(node[1]), node[2]))
    if ((0 <= (node[0]-1) < len(grid)) and (0 <= (node[1]) < len(grid))):
        if not grid[node[0]-1][node[1]].obstacle:
            neigh.append(((node[0]-1),(node[1]), node[2]))
    if ((0 <= (node[0]) < len(grid)) and (0 <= (node[1]+1) < len(grid))):
        if  not grid[node[0]][node[1]+1].obstacle:
            neigh.append(((node[0]),(node[1]+1), node[2]))
    if ((0 <= (node[0]) < len(grid)) and (0 <= (node[1]-1) < len(grid))):
        if not grid[node[0]][node[1]-1].obstacle:
            neigh.append(((node[0]),(node[1]-1), node[2]))
    
    return neigh

#calculated an estimated distance to the goal
def heuristic(goal, node):
    (x1, y1 , z1) = goal
    (x2, y2, z2) = node
    return abs(x1-x2) + abs(y1-y2) + abs(z1-z2)