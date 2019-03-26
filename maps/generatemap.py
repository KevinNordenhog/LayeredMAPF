import sys
import math
import argparse
import random
                
#########################
# Parse arguments
#########################
try:
    parser = argparse.ArgumentParser(
            description="""Output a world config file of user specified size
            (default 20x20). The density of how often objects appear can be
            selected (default 10%)""")
    parser.add_argument("size", help="size of grid (size x size)", type=int)
    parser.add_argument("density", help="obstacle density (0-100)", type=int)
    parser.add_argument("agents", help="number of agents", type=int)
    parser.add_argument("dynamic_density", help="""If dynamic density is > 0,
            dynamic objects may spawn at random locations during simulation. Input
            (0-100)""", type=int)
    parser.add_argument("probability", help="""Probability of a dynamic object
    spawning at each time step (0-100)""", type=int)
    #parser.set_defaults(size=20, density=10, agents=1)
    args = parser.parse_args()
except:
    e = sys.exc_info()[0]
    print (e)

#########################
# Agent configuration
#########################
agent_config = "agents:\n"
a_goals = []
a_start = []
for agent in range(args.agents):
    pos_found = False
    while not pos_found:
        goal = (random.randint(0,args.size-1), random.randint(0,args.size-1))
        start = (random.randint(0,args.size-1), random.randint(0,args.size-1))
        pos_found = not (start in a_start or goal in a_goals)
    a_goals += [goal]
    a_start += [start]
    # Add agent to config
    agent_config += "-   goal: [%d, %d]\n" %  (goal[0], goal[1])
    agent_config += "    name: agent%d\n" % (agent)
    agent_config += "    start: [%d, %d]\n" % (start[0], start[1])

#########################
# Map configuration
#########################
map_config = "map:\n"
map_config += "    dimensions: [%d, %d]\n" % (args.size, args.size)
map_config += "    obstacles:\n"
# Generate obstacles (not on agent starting points or goals)
no_obstacles = int(math.floor(args.size*args.size*0.01*args.density))
obstacles = []
for obstacle in range(no_obstacles):
    pos_found = False
    while not pos_found:
        pos = (random.randint(0,args.size-1), random.randint(0,args.size-1))
        pos_found = not (pos in a_goals or pos in a_start)
    obstacles += [pos]
obstacles.sort()
for obs in obstacles:
    map_config += "    - !!python/tuple [%d, %d]\n" % (obs[0], obs[1])
# Add dynamic obstacle to config
map_config += "    dynamic_obstacles:\n"
no_dynamic = int(math.floor(args.size*args.size*0.01*args.dynamic_density))
dynamic_obstacles = []
for obstacle in range(no_dynamic):
    pos_found = False
    while not pos_found:
        pos = (random.randint(0,args.size-1), random.randint(0,args.size-1))
        pos_found = not (pos in a_goals or pos in a_start or pos in obstacles)
    dynamic_obstacles += [pos+(args.probability,)]
dynamic_obstacles.sort()
for obs in dynamic_obstacles:
    map_config += "    - !!python/tuple [%d, %d, %d]\n" % (obs[0], obs[1], obs[2])

#########################
# Output map to file
#########################
config = agent_config + map_config
name = "map_s%d_a%d_d%d.yaml" % (args.size, args.agents, args.density)
f = open(name, "w")
f.write(config)

