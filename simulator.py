#!/usr/bin/env python3
import yaml
import matplotlib
import argparse

#import numpy as np
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
        self.agents = self.creatagents(world)  #[] eller {} ??
        planner = GlobalPlanner(self.grid.grid, self.agents)  # dict (agent:  [path])
        self.schedule = planner.schedule

        aspect = world["map"]["dimensions"][0] / world["map"]["dimensions"][1]

        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

        self.patches = []

        #Grid setup
        xmin = 0
        ymin = 0
        xmax = world["map"]["dimensions"][0] - xmin
        ymax = world["map"]["dimensions"][1] - ymin
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))       
        #Draw walls
        for row in self.grid.grid:
            for cell in row:
                if cell.obstacle:
                    #print (cell.x, cell.y)
                    self.patches.append(Rectangle((cell.x, cell.y), 1, 1, facecolor='red', edgecolor='black'))
        
        for cell in self.schedule:
            self.patches.append(Rectangle((cell[0], cell[1]), 1, 1, facecolor='blue', edgecolor='black'))


        for p in self.patches:
            self.ax.add_patch(p)
        
        # self.T=0
        # #matplotlib function that repeatedly calles a function func, frames is the parameter(s)
        # self.anim = animation.FuncAnimation(self.fig, self.simulate,
        #                       init_func=self.init_func,
        #                       frames=int(self.T+1) * 10,
        #                       interval=100,
        #                       blit=True)

    def creatagents(self, world):
        agents = []
        for agent in world["agents"]:
            name = agent["name"]
            goal = (agent["goal"][0],agent["goal"][1])
            start = (agent["start"][0],agent["start"][1])
            a = Agent(name, goal, start)
            agents.append(a)
            # print (a.name)
            # print (a.goal)
            # print (a.pos)
        return agents

    def simulate(self, i):
        pass
    
    # def init_func(self):
    #     for p in self.patches:
    #         self.ax.add_patch(p)
    #     # for a in self.artists:
    #     #     self.ax.add_artist(a)
    #     return self.patches #+ self.artists


    def show(self):
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    args = parser.parse_args()


    with open(args.map) as map_file:
        world = yaml.load(map_file)
    
    print (world)

    simulator = Simulator(world)

    simulator.show()


    