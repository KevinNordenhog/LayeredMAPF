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
        self.width, self.heigth = world["map"]["dimensions"]
        for i in range(0,self.width):
            grid.append([])
            for j in range(0,self.heigth):
                cell = Cell(i,j)
                if (i,j) in world["map"]["obstacles"]:
                    cell.obstacle = True
                grid[i].append(cell)
        self.grid = grid



   
