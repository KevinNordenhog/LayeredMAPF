import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class GlobalPlanner:
    def __init__(self, grid, agents):
        #print (grid)
        if len(agents) == 1:
            #start = grid[agents[0].x][agents[0].y]
            #goal = grid[agents[0].goal[0]][agents[0].goal[1]]
            self.schedule = self.aStar(grid, agents[0].pos, agents[0].goal)
    
    def aStar(self, grid, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        path = []
        
        print (goal)

        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break
            
            for node in self.neighbours(grid, current):
                new_cost = cost_so_far[current] + 1
                if node not in cost_so_far or new_cost < cost_so_far[node]:
                    cost_so_far[node] = new_cost
                    prio = new_cost + self.heuristic(goal, node)
                    frontier.put(node, prio)
                    came_from[node] = current
                    

        temp = current
        while (temp in came_from):
            path.append(temp)
            temp = came_from[temp]
        return path

    def neighbours(self, grid, node):
        neigh = []
        if ((0 <= (node[0]+1) < len(grid)) and (0 <= (node[1]) < len(grid))):
            if not grid[node[0]+1][node[1]].obstacle:
                neigh.append(((node[0]+1),(node[1])))
        if ((0 <= (node[0]-1) < len(grid)) and (0 <= (node[1]) < len(grid))):
            if not grid[node[0]-1][node[1]].obstacle:
                neigh.append(((node[0]-1),(node[1])))
        if ((0 <= (node[0]) < len(grid)) and (0 <= (node[1]+1) < len(grid))):
            if  not grid[node[0]][node[1]+1].obstacle:
                neigh.append(((node[0]),(node[1]+1)))
        if ((0 <= (node[0]) < len(grid)) and (0 <= (node[1]-1) < len(grid))):
            if not grid[node[0]][node[1]-1].obstacle:
                neigh.append(((node[0]),(node[1]-1)))
        
        return neigh

    #calculated an estimated distance to the goal
    def heuristic(self, goal, node):
        (x1, y1) = goal
        (x2, y2) = node
        return abs(x1-x2) + abs(y1-y2)