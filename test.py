import generatemap
import simulator
import yaml

if __name__ == "__main__":
    size = 5
    density = 0
    agents = 4
    dynamic_density = 0
    dynamic_probability = 0
    global_planner = "cbs"
    delays = True
    animate = False
    prob_delay = 20

    map_config = generatemap.gen_map(size, density, agents,
            dynamic_density, dynamic_probability)
    generatemap.save_map(map_config, "maps/test_map.yaml")
    world = yaml.load(map_config)

    sim = simulator.Simulator(world, global_planner, 0)
    sim.simulate(delays, animate, prob_delay)
