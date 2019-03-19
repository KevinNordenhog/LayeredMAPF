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
        (2,7), (2,7), (3,7)]
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
            # Make agent red if goal is unreachable
            if not agent.goal in self.schedule[agent.name]:
                self.circles[agent.name].original_face_color = 'red'
                continue
            # Update position
            pos = self.updatePos(agent) 
            self.circles[agent.name].center = pos
        # Updates the circles according to new positions
        for agent in self.agents:
            self.circles[agent.name].set_facecolor(self.circles[agent.name].original_face_color)
    

    # Move the agent towards the next position 0.1 step at a time
    # Return the position after step is taken.
    def updatePos(self, agent):
        currentP = self.circles[agent.name].center # the circles position
        if agent.pos == agent.goal:
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
        # Otherwise, update and return new position
        newpos = tuple(map(operator.add,
                currentP,(0.1*(nxt[0]-curr[0]),0.1*(nxt[1]-curr[1]))))
        newpos = (round(newpos[0],1), round(newpos[1],1))
        # If agent reached next pos, increment it one step
        if (newpos == tuple(map(operator.add, nxt, (0.5,0.5)))):
            agent.pos = nxt
            agent.step += 1
        return newpos

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    args = parser.parse_args()


    with open(args.map) as map_file:
        world = yaml.load(map_file)

    simulator = Simulator(world)
    simulator.simulate()
