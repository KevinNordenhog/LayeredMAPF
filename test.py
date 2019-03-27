import generatemap
import simulator
import yaml

if __name__ == "__main__":
    size = 10
    density = 20
    agents = 5
    dynamic_density = 10
    dynamic_probability = 10
    global_planner = "cbs"
    world = yaml.load(generatemap.gen_map(size, density, agents,
            dynamic_density, dynamic_probability))
    sim = simulator.Simulator(world, global_planner)
    sim.dynamic = True
    sim.simulate()
