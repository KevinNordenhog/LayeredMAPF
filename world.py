class Cell:
    obstacle = False
    occupied = False
    def __init__(self, x, y):
        self.pos = (x, y)
        self.x = x
        self.y = y


class Grid:
    def __init__(self, world):
        grid = []
        x,y = world["map"]["dimensions"]
        for i in range(0,x):
            grid.append([])
            for j in range(0,y):
                cell = Cell(i,j)
                if (i,j) in world["map"]["obstacles"]:
                    #cell.color = black
                    cell.obstacle = True
                grid[i].append(cell)
        
        self.grid = grid



   