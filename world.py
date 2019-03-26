class Cell:
    obstacle = False
    occupied = False
    def __init__(self, x, y):
        self.pos = (x, y)
        self.x = x
        self.y = y


class Grid:
    def __init__(self, world):
        self.dynamic_obs = []
        self.width, self.heigth = world["map"]["dimensions"]
        self.grid = [[Cell(j,i) for i in range(self.width)] for j in range(self.heigth)]
        if world["map"]["obstacles"]:
            for obs in world["map"]["obstacles"]:
                self.grid[obs[0]][obs[1]].obstacle = True
        if world["map"]["dynamic_obstacles"]:
            for dyn in world["map"]["dynamic_obstacles"]:
                self.dynamic_obs += [dyn]




   
