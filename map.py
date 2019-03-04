


#Colors in rgb
black = (0,0,0,)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

class Cell:

    obsticle = False
    occupied = False

    def __init__(self, x, y, size):
        self.pos = (x, y)
        self.size = size


    def setColor(self, color):
        self.color = color


    def setObsticle(self, obsticle):
        self.obsticle = obsticle
        if (obsticle):
            self.color = black
        # elif (self.start):
        #     self.color = green
        # elif (self.goal):
        #     self.color = red
        else:
            self.color = white


def generateMap:
    return