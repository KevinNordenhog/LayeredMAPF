#!/usr/bin/env python3
import yaml
import matplotlib
import argparse
import operator
import time
import random
import sys

# Plot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.collections as mcoll
from matplotlib.patches import Circle, Rectangle, Arrow


from agent import Agent
from world import Grid, Cell
from planner import Planner


class Simulator:
    def __init__(self, world, alg, tolerance):
        self.delays = True
        self.animate = False
        self.delay_probability = 5
        self.dynamic = True if world["map"]["dynamic_obstacles"] else False
        self.grid = Grid(world)        
        self.agents = createagents(world)
        self.planner = Planner(self.grid, self.agents, alg, tolerance)
        self.schedule = self.planner.schedule

    # Start the simulation, plot the grid and update it continously
    def simulate(self):
        self.stepcount = 0
        if self.animate:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111, aspect='equal')
            self.createfig()
            self.rendercount = 0
            plt.xlim(0, self.grid.heigth)
            plt.ylim(0, self.grid.width)
            ani = animation.FuncAnimation(self.fig, self.update, interval=50)
            plt.show()
        # Used for testing without graphical interface
        else:
            while not simulation_finished(self.agents):
                # Create deviations
                deviations = self.deviate()
                if deviations:
                    print ("\nDeviation occured on time %s at %s." % (self.stepcount,deviations))
                    recalc = self.planner.localplanner(deviations, self.grid, self.agents)
                    if recalc:
                        self.schedule = self.planner.schedule
                self.stepcount += 1
                # Move agents
                for agent in self.agents.values():
                    if (agent.pos == agent.goal and 
                            not self.schedule[agent.name]):
                        continue
                    curr = agent.pos
                    nxt = self.schedule[agent.name][0]
                    self.grid.grid[agent.x][agent.y].occupied = False
                    agent.pos = nxt
                    agent.x, agent.y = agent.pos[0], agent.pos[1]
                    self.grid.grid[agent.x][agent.y].occupied = True
                    agent.step += 1
                    self.schedule[agent.name].pop(0)
            
            # Goal reached, evaluate performance
            self.planner.evaluate(self.grid, self.agents)

    # Create deviations and run local planner if necessary,
    # then move agents and update figure
    def update(self, *args):
        if simulation_finished(self.agents):
            self.planner.evaluate(self.grid, self.agents)
            sys.exit()
        if (self.rendercount % 10) == 0:
            deviations = self.deviate()
            if deviations:
                print ("\nDeviation occured on time %s at %s." % (self.stepcount,deviations))
                recalc = self.planner.localplanner(deviations, self.grid, self.agents)
                if recalc:
                    self.schedule = self.planner.schedule
                self.createfig()
            self.stepcount += 1
        self.updatefig()
        self.rendercount += 1

    # Create deviations if dynamic blocks or delays are turned on
    def deviate(self):
        deviations = []
        # Spawn dynamic blocks based their probability
        if self.dynamic:
            for (x,y,probability) in self.grid.dynamic_obs:
                if (self.grid.grid[x][y].occupied
                        or self.grid.grid[x][y].obstacle):
                    continue
                if probability > random.randint(0,100):
                    deviations += [(x,y)]
                    self.grid.grid[x][y].obstacle = True
        # Delay agents based on delay probability
        if self.delays:
            for agent in self.agents.values():
                if random.randint(0,100) < self.delay_probability:
                    deviations += [agent.name]
                    self.schedule[agent.name].insert(0, agent.pos)
                    agent.delay += 1
        return deviations

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
        for agent in self.agents.values():
            self.circles[agent.name] = Circle(
                (agent.x+0.5, agent.y+0.5), 0.3, facecolor='blue', edgecolor='black')
            self.circles[agent.name].facecolor = 'yellow'
            patches.append(self.circles[agent.name])
        # Update subplot
        [p.remove() for p in reversed(self.ax.patches)]
        for p in patches:
            self.ax.add_patch(p)


    # Update the figure to show moving agents
    def updatefig(self):
        for agent in self.agents.values():
            # Move agent positions according to schedule
            pos = self.updatePos(agent) 
            self.circles[agent.name].center = pos
            # Color the agents
            if (agent.pos == agent.goal and
                    not self.schedule[agent.name]):
                self.circles[agent.name].facecolor = 'lightgreen'
            elif not agent.goal in self.schedule[agent.name]:
                self.circles[agent.name].facecolor = 'red'
            elif agent.delay:
                self.circles[agent.name].facecolor = 'orange'
        # Updates the figure
        for agent in self.agents.values():
            self.circles[agent.name].set_facecolor(self.circles[agent.name].facecolor)
    

    # Move the agent towards the next position 0.1 step at a time
    # Return the position after step is taken.
    def updatePos(self, agent):
        currentP = self.circles[agent.name].center # the circles position
        if (agent.pos == agent.goal and 
                not self.schedule[agent.name]):
            return currentP
        # Handle wait
        agent.rendercount += 1
        if agent.iswaiting:
            agent.iswaiting = agent.rendercount % 10
            if not agent.iswaiting:
                agent.step += 1
            return currentP
        curr = agent.pos
        nxt = self.schedule[agent.name][0]
        if curr == nxt:
            agent.iswaiting = True
            self.schedule[agent.name].pop(0)
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
            self.schedule[agent.name].pop(0)
        return newpos

# Create a dictonary containing all agents
def createagents(world):
    agents = {}
    for agent in world["agents"]:
        name = agent["name"]
        goal = (agent["goal"][0],agent["goal"][1])
        start = (agent["start"][0],agent["start"][1])
        agents[name] = Agent(name, goal, start)
    return agents

# Check if all agents have reached their goals
def simulation_finished(agents):
    finished = True
    for agent in agents.values():
        if agent.pos != agent.goal:
            finished = False
    return finished

# Parse input and run simulator
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    parser.add_argument("alg", help="algorithms: cbs, castar")
    args = parser.parse_args()
    delay_tolerance = 1


    with open(args.map) as map_file:
        world = yaml.load(map_file)
    
    simulator = Simulator(world, args.alg, delay_tolerance)
    simulator.simulate()
