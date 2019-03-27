#!/usr/bin/env python3
import yaml
import matplotlib
import argparse
import operator
import time
import random

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
    def __init__(self, world, alg):
        if world["map"]["dynamic_obstacles"]:
            self.dynamic = True
        else:
            self.dynamic = False
        self.grid = Grid(world)        
        self.agents = self.createagents(world)
        self.alg = alg
        # Execute global planner and measure time
        print ("Global planner executing.")
        start = time.time()
        self.planner = GlobalPlanner(self.grid.grid, self.agents, self.alg)
        end = time.time()
        self.schedule = self.planner.schedule
        self.evaluate_planner(self.planner, end, start)


    def evaluate_planner(self, planner, end, start):
        # Evaluate execution 
        print ("----------------------------------")
        print ("Planner: %s" % planner.planner)
        print ("Execution time: %f" % (end-start))
        print ("Number of agents: %d" % len(self.agents))
        print ("Size of grid: %dx%d" % (self.grid.width, self.grid.heigth))
        success_cnt = 0
        for agent in self.agents:
            if self.schedule[agent.name]:
                success_cnt += 1
        completion = 100*(success_cnt/len(self.agents))
        print ("Completion rate: %d%%" % completion)
        print ("Makespan: %d" % (len(max(self.schedule.values(), key=lambda
                schedule: len(schedule)))))
        print ("----------------------------------")

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
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.createfig()
        plt.xlim(0, self.grid.heigth)
        plt.ylim(0, self.grid.width)
        self.rendercount = 0
        self.stepcount = 0
        ani = animation.FuncAnimation(self.fig, self.update, interval=50)
        plt.show()
    
    # Run the local planner
    def update(self, *args):
        if (self.rendercount % 10) == 0:
            deviations = self.deviate()
            if deviations:
                print ("")
                print ("Deviation occured on time %s at %s." % (self.stepcount,deviations))
                print ("Local planner executing")
                start = time.time()
                self.localplanner()
                end = time.time()
                self.evaluate_planner(self.planner, end, start)
                self.createfig()
            self.stepcount += 1
        self.updatefig()
        self.rendercount += 1

    # Randomly spawn blocks at locations where deviations may occur
    # Input: Location of deviations, probability of deviation
    # Output: List of deviations [(x,y)]
    def deviate(self):
        if not self.dynamic:
            return []
        deviations = []
        for (x,y,probability) in self.grid.dynamic_obs:
            if (self.grid.grid[x][y].occupied
                    or self.grid.grid[x][y].obstacle):
                continue
            if probability > random.randint(0,100):
                deviations += [(x,y)]
                self.grid.grid[x][y].obstacle = True
        return deviations

    def localplanner(self):
        for agent in self.agents:
            agent.step = 0
        planner = GlobalPlanner(self.grid.grid, self.agents, self.alg)
        self.schedule = planner.schedule
        
    # Create patches that visualizes the grid
    def createfig(self):
        patches = []
        # Create white background
        patches.append(Rectangle(
            (0, 0), self.grid.heigth, self.grid.width, facecolor='none', edgecolor='red'))       
        # Add obstacles
        for row in self.grid.grid:
            for cell in row:
                if cell.obstacle:
                    patches.append(Rectangle(
                        (cell.x, cell.y), 1, 1, facecolor='red', edgecolor='black'))
        # Add schedule given by path finding algorithm
        for agent in self.schedule:
            for cell in self.schedule[agent]:
                patches.append(Rectangle(
                    (cell[0], cell[1]), 1, 1, alpha=0.2, facecolor='blue', edgecolor='black'))
        # Add agents to grid
        self.circles = {}
        for agent in self.agents:
            self.circles[agent.name] = Circle(
                (agent.x+0.5, agent.y+0.5), 0.3, facecolor='orange', edgecolor='black')
            self.circles[agent.name].facecolor = 'orange'
            patches.append(self.circles[agent.name])
        # Update subplot
        [p.remove() for p in reversed(self.ax.patches)]
        for p in patches:
            self.ax.add_patch(p)


    # Update the figure to show moving agents
    def updatefig(self):
        for agent in self.agents:
            # Goal unreachable / reached
            if not agent.goal in self.schedule[agent.name]:
                self.circles[agent.name].facecolor = 'red'
                continue
            if (agent.pos == agent.goal and
                    agent.step == len(self.schedule[agent.name])-1):
                self.circles[agent.name].facecolor = 'lightgreen'
            # Update position
            pos = self.updatePos(agent) 
            self.circles[agent.name].center = pos
        # Updates the circles according to new positions and colors
        for agent in self.agents:
            self.circles[agent.name].set_facecolor(self.circles[agent.name].facecolor)
    

    # Move the agent towards the next position 0.1 step at a time
    # Return the position after step is taken.
    def updatePos(self, agent):
        currentP = self.circles[agent.name].center # the circles position
        if (agent.pos == agent.goal and 
                agent.step == len(self.schedule[agent.name])-1):
            return currentP
        curr = self.schedule[agent.name][agent.step]
        nxt = self.schedule[agent.name][agent.step+1]
        # Handle wait
        agent.rendercount += 1
        if agent.iswaiting:
            agent.iswaiting = agent.rendercount % 10
            if not agent.iswaiting:
                agent.step += 1
            return currentP
        if curr == nxt:
            agent.iswaiting = True
            return currentP
        # Update and return new position
        newpos = tuple(map(operator.add,
                currentP,(0.1*(nxt[0]-curr[0]),0.1*(nxt[1]-curr[1]))))
        newpos = (round(newpos[0],1), round(newpos[1],1))
        # If agent reached next pos, increment it one step
        if (newpos == tuple(map(operator.add, nxt, (0.5,0.5)))):
            self.grid.grid[agent.x][agent.y].occupied = False
            agent.pos = nxt
            agent.x, agent.y = agent.pos[0], agent.pos[1]
            self.grid.grid[agent.x][agent.y].occupied = True
            agent.step += 1
        return newpos

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    parser.add_argument("alg", help="algorithmss: cbs, castar")
    args = parser.parse_args()


    with open(args.map) as map_file:
        world = yaml.load(map_file)
    
    simulator = Simulator(world, args.alg)
    simulator.simulate()
