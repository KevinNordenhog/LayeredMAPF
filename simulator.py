#!/usr/bin/env python3
import yaml
import matplotlib
import argparse
import operator

# Plot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.collections as mcoll
from matplotlib.patches import Circle, Rectangle, Arrow


from agent import Agent
from world import Grid, Cell
from globalPlanner import GlobalPlanner


class Simulator:
    def __init__(self, world):
        print "Initialization..."
        self.grid = Grid(world) #[[object, object],[]] NOTE: grid.grid[x][y]        
        self.agents = self.createagents(world)  #[] eller {} ??
        planner = GlobalPlanner(self.grid.grid, self.agents)  # dict (agent:  [path])
        self.schedule = planner.schedule
        print ("Global planner finished executing.")

    def createagents(self, world):
        agents = []
        for agent in world["agents"]:
            name = agent["name"]
            goal = (agent["goal"][0],agent["goal"][1])
            start = (agent["start"][0],agent["start"][1])
            agents.append(Agent(name, goal, start))
        return agents

    # Start the simulation, plot the grid and update it continously
    def simulate(self):
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, aspect='equal')
        patches = []
        plt.xlim(0, self.grid.heigth)
        plt.ylim(0, self.grid.width)
        patches.append(Rectangle(
            (0, 0), self.grid.heigth, self.grid.width, facecolor='none', edgecolor='red'))       
        # Show static world (open or obstacle)
        for row in self.grid.grid:
            for cell in row:
                if cell.obstacle:
                    patches.append(Rectangle(
                        (cell.x, cell.y), 1, 1, facecolor='red', edgecolor='black'))
        #Show schedule given by path finding algorithm
        for agent in self.schedule:
            for cell in self.schedule[agent]:
                patches.append(Rectangle(
                    (cell[0], cell[1]), 1, 1, alpha=0.2, facecolor='blue', edgecolor='black'))
        
        self.circles = {}
        for agent in self.agents:
            self.circles[agent.name] = Circle(
                (agent.x+0.5, agent.y+0.5), 0.3, facecolor='orange', edgecolor='black')
            self.circles[agent.name].original_face_color = 'orange'

            patches.append(self.circles[agent.name])

        # Animate and plot
        for p in patches:
            ax.add_patch(p)
        #self.step = 0
        ani = animation.FuncAnimation(self.fig, self.update, interval=50)
        plt.show()
    
    # Run the local planner
    def update(self, *args):
        #if deviation():
        #    localplanner()
        #moveagents()
        self.updatefig(self, *args)
        

    # Update the figure to show the current grid
    def updatefig(self, *args):
        for agent in self.agents:
            pos = self.getPos(agent) 
            self.circles[agent.name].center = pos#tuple(map(operator.add, pos,(0.5, 0.5)))
        #updates the circles
        for agent in self.agents:
            self.circles[agent.name].set_facecolor(self.circles[agent.name].original_face_color)
    

    def getPos(self, agent):
        currentP = self.circles[agent.name].center # the circles position
        if not agent.pos == agent.goal:
            curr = self.schedule[agent.name][agent.step]
            if not curr == agent.goal:
                nxt = self.schedule[agent.name][agent.step+1]
                currentP = tuple(map(operator.add,
                        currentP,(0.1*(nxt[0]-curr[0]),0.1*(nxt[1]-curr[1]))))
                currentP = self.roundTuple(currentP)
                if (currentP == tuple(map(operator.add, nxt, (0.5,0.5)))):
                    agent.step += 1
         

        return currentP

    def roundTuple(self, tup):
        return (round(tup[0],1), round(tup[1],1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    args = parser.parse_args()


    with open(args.map) as map_file:
        world = yaml.load(map_file)

    simulator = Simulator(world)
    simulator.simulate()
