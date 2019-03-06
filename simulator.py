#!/usr/bin/env python3
import yaml
import matplotlib
import argparse

# Plot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.collections as mcoll
from matplotlib.patches import Circle, Rectangle, Arrow


import agent
from agent import Agent
import world
from world import Grid, Cell
import globalPlanner
from globalPlanner import GlobalPlanner


class Simulator:
    def __init__(self, world):
        self.grid = Grid(world) #[[object, object],[]] NOTE: grid.grid[x][y]        
        self.agents = self.createagents(world)  #[] eller {} ??
        planner = GlobalPlanner(self.grid.grid, self.agents)  # dict (agent:  [path])
        self.schedule = planner.schedule
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.patches = []

    def createagents(self, world):
        agents = []
        for agent in world["agents"]:
            name = agent["name"]
            goal = (agent["goal"][0],agent["goal"][1])
            start = (agent["start"][0],agent["start"][1])
            agents.append(Agent(name, goal, start))
        return agents


    def simulate(self, world):
        pass

    def show(self):
        heigth = len(self.grid.grid)
        width = len(self.grid.grid[0])
        plt.xlim(0, heigth)
        plt.ylim(0, width)
        self.patches.append(Rectangle(
            (0, 0), heigth, width, facecolor='none', edgecolor='red'))       
        #Draw walls
        for row in self.grid.grid:
            for cell in row:
                if cell.obstacle:
                    self.patches.append(Rectangle(
                        (cell.x, cell.y), 1, 1, facecolor='red', edgecolor='black'))
                
        for cell in self.schedule:
            self.patches.append(Rectangle(
                (cell[0], cell[1]), 1, 1, facecolor='blue', edgecolor='black'))

        for p in self.patches:
            self.ax.add_patch(p)        

        ani = animation.FuncAnimation(self.fig, self.updatefig)
        plt.show()


    def updatefig(self, *args):
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    args = parser.parse_args()


    with open(args.map) as map_file:
        world = yaml.load(map_file)
    
    simulator = Simulator(world)
    simulator.show()

