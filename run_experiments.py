import generatemap
import simulator
import yaml
import time
import signal



class Timeout(Exception):
    pass

def handler(sig, frame):
    raise Timeout

# * Agents k=3 to 13
# * 100 instances per test
# * Test should be run on cbs or tail cbs with tolerance 1-4
# * Discard instances that take over 5 minutes

if __name__ == "__main__":
    test_no = 0
    start = time.time()
    runtime = []
    nodes = []
    failed_tests = 0
    while test_no < 100:
        # Test parameters
        size = 8
        density = 0
        agents = 8
        global_planner = "cbs"
        # Generate map
        map_config = generatemap.gen_map(size, density, agents, 0, 0)
        generatemap.save_map(map_config, "maps/experiment_map.yaml")
        world = yaml.load(map_config)
        # Count time
        t = time.time()
        test_no += 1
        # Set timeout to 5min
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(500)
        # Run algorithm
        try:
            sim = simulator.Simulator(world, global_planner)
            # Save runtime data
            nodes += [sim.planner.node_cnt]
            runtime += [time.time()-t]
        except Timeout:
            failed_tests += 1
            print("Took too long (>5 minutes)")

    print ("Test finished.")
    tot_time = time.time()-start
    print ("Total time: %f" % tot_time)
    avg_nodes = sum(nodes)/len(nodes)
    print ("Average generated nodes: %d" % avg_nodes)
    avg_runtime = sum(runtime)/len(runtime)
    print ("Average run-time: %f" % avg_runtime)
    print ("Successful rate: %d%%" % (100-failed_tests))
