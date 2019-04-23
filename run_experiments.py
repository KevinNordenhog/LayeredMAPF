import generatemap
import simulator
import yaml
import random

if __name__ == "__main__":
    while 1:
        size = 32
        density = 20
        agents = random.randint(2,15)
        global_planner = "cbs"

        map_config = generatemap.gen_map(size, density, agents, 0, 0)
        generatemap.save_map(map_config, "maps/experiment_map.yaml")
        world = yaml.load(map_config)

        sim = simulator.Simulator(world, global_planner)
        sim.delays = True
        sim.simulate()
