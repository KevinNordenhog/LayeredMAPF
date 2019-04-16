class Agent:
     def __init__(self, name, goal, pos):
        self.name = name
        self.start = pos
        self.goal = goal
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.step = 0
        # Used for rendering in simulator
        self.rendercount = 0
        self.iswaiting = False
        self.delay = 0
