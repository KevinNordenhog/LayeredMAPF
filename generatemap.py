import sys
import math
import argparse
import random


#########################
# Create configuration
#########################
def create_config(agents, size, density, dynamic_density, probability):
    #####################
    # Agent configuration
    #####################
    agent_config = "agents:\n"
    a_goals = []
    a_start = []
    for agent in range(agents):
        pos_found = False
        while not pos_found:
            goal = (random.randint(0,size-1), random.randint(0,size-1))
            start = (random.randint(0,size-1), random.randint(0,size-1))
            pos_found = not (start in a_start or goal in a_goals)
        a_goals += [goal]
        a_start += [start]
        agent_config += "-   goal: [%d, %d]\n" %  (goal[0], goal[1])
        agent_config += "    name: agent%d\n" % (agent)
        agent_config += "    start: [%d, %d]\n" % (start[0], start[1])
    ###################
    # Map configuration
    ###################
    map_config = "map:\n"
    map_config += "    dimensions: [%d, %d]\n" % (size, size)
    map_config += "    obstacles:\n"
    # Generate obstacles (not on agent starting points or goals)
    no_obstacles = int(math.floor(size*size*0.01*density))
    obstacles = []
    for obstacle in range(no_obstacles):
        pos_found = False
        while not pos_found:
            pos = (random.randint(0,size-1), random.randint(0,size-1))
            pos_found = not (pos in a_goals or pos in a_start)
        obstacles += [pos]
    obstacles.sort()
    for obs in obstacles:
        map_config += "    - !!python/tuple [%d, %d]\n" % (obs[0], obs[1])
    # Add dynamic obstacle to config
    map_config += "    dynamic_obstacles:\n"
    no_dynamic = int(math.floor(size*size*0.01*dynamic_density))
    dynamic_obstacles = []
    for obstacle in range(no_dynamic):
        pos_found = False
        while not pos_found:
            pos = (random.randint(0,size-1), random.randint(0,size-1))
            pos_found = not (pos in a_goals or pos in a_start or pos in obstacles)
        dynamic_obstacles += [pos+(probability,)]
    dynamic_obstacles.sort()
    for obs in dynamic_obstacles:
        map_config += "    - !!python/tuple [%d, %d, %d]\n" % (obs[0], obs[1], obs[2])
    config = agent_config + map_config
    return config


#########################
# Warehouse config
#########################
def create_warehouse(agents):
    rows = 20
    cols = 21
    ###################
    # Map configuration
    ###################
    map_config = "map:\n"
    map_config += "    dimensions: [%d, %d]\n" % (rows, cols)
    map_config += "    obstacles:\n"
    # Generate warehouse obstacles
    positions = [(2,2), (5,2), (8,2), (11,2), (14,2), (17,2),
            (2,11), (5,11), (8,11), (11,11), (14,11), (17,11)]
    obstacles = []
    for x, y in positions:
        for i in range (2):
            for j in range(7):
                obstacles += [(x+i, y+j)]
    for obs in obstacles:
        map_config += "    - !!python/tuple [%d, %d]\n" % (obs[0], obs[1])
    map_config += "    dynamic_obstacles:\n"
    # Generate agents
    agent_config = "agents:\n"
    a_goals = []
    a_start = []
    for agent in range(agents):
        pos_found = False
        while not pos_found:
            goal = (random.randint(0,cols-1), random.randint(0,rows-1))
            start = (random.randint(0,cols-1), random.randint(0,rows-1))
            pos_found = not (
                    start in a_start 
                    or goal in a_goals
                    or start in obstacles
                    or goal in obstacles)
        a_goals += [goal]
        a_start += [start]
        agent_config += "-   goal: [%d, %d]\n" %  (goal[0], goal[1])
        agent_config += "    name: agent%d\n" % (agent)
        agent_config += "    start: [%d, %d]\n" % (start[0], start[1])
    # Return config
    config = agent_config + map_config
    return config


#########################
# Output map to file
#########################
def save_map(config, name):
    f = open(name, "w")
    f.write(config)

#########################
# Generate map based on input and save to maps/ folder
#########################
def gen_map(size, density, agents, dynamic_density, probability):
    if size == "warehouse":
        config = create_warehouse(agents)
    else:
        config = create_config(agents, size, density, dynamic_density, probability)
    return config

#########################
# Main function
#########################
if __name__ == "__main__":
    # Parse arguments
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
    config = gen_map(args.size, args.density, args.agents, 
            args.dynamic_density, args.probability)
    name = "maps/map_s%d_a%d_d%d.yaml" % (args.size, args.agents, args.density)
    save_map(config, name)
