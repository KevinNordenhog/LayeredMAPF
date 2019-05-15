import generatemap
import simulator
import yaml
import time
import signal
import sys
import math


class Timeout(Exception):
    pass

def handler(sig, frame):
    raise Timeout

def variance(values):
    mean = sum(values)/len(values)
    num = 0
    for val in values:
        num += pow((val-mean), 2)
    variance = math.sqrt(num/len(values))
    return variance

# * Agents k=3 to 13
# * 100 instances per test
# * Test should be run on cbs or tail cbs with tolerance 1-4
# * Discard instances that take over 5 minutes


def test(agents, delay_tolerance, global_planner, genmap):
    # Test parameters
    test_no = 100
    size = 10
    density = 0
    # Generate map
    if genmap:
        for i in range(test_no):
            map_config = generatemap.gen_map(size, density, agents, 0, 0)
            generatemap.save_map(map_config, "maps/experiments/map%d.yaml" % i)
            world = yaml.load(map_config)

    # Run and evaluate algorithm on 100 maps
    start = time.time()
    runtime = []
    nodes = []
    sic = []
    makespan = []
    failed_tests = 0
    for i in range(test_no):
        # Load map
        with open("maps/experiments/map%d.yaml" % i) as map_file:
            world = yaml.load(map_file)
        # Count time
        t = time.time()
        test_no += 1
        # Set timeout to 5min
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(300)
        # Run algorithm
        try:
            print ("\nRunning test %d" % i)
            sim = simulator.Simulator(world, global_planner, delay_tolerance)
            # Save runtime data
            nodes += [sim.planner.node_cnt]
            sic += [sim.planner.cost]
            makespan += [sim.planner.makespan]
            runtime += [time.time()-t]
        except Timeout:
            failed_tests += 1
            print("Took too long (>5 minutes)")

    nodes = sorted(nodes)
    sic = sorted(sic)
    makespan = sorted(makespan)
    runtime = sorted(runtime)
    print ("\nTest finished.")
    tot_time = time.time()-start
    print ("Total time: %.6f" % tot_time)
    print ("Successful rate: %d%%" % (100-failed_tests))
    avg_nodes = sum(nodes)/len(nodes)
    avg_runtime = sum(runtime)/len(runtime)
    avg_sic = sum(sic)/len(sic)
    avg_makespan = sum(makespan)/len(makespan)
    median_nodes = nodes[49]
    median_runtime = runtime[49]
    median_sic = sic[49]
    median_makespan = makespan[49]
    results = "\n"
    results += "Tolerance: %d\n" % delay_tolerance
    results += "Total time: %.6f" % tot_time
    results += "Successful rate: %d%%" % (100-failed_tests)
    results += "Average run-time: %.6f\n" % avg_runtime
    results += "Median run-time: %.6f\n" % median_runtime
    results += "Variance (runtime): %.6f\n" % variance(runtime)
    results += "Average generated nodes: %d\n" % avg_nodes
    results += "Median generated nodes: %d\n" % median_nodes
    results += "Average sic: %.2f\n" % avg_sic
    results += "Median sic: %.2f\n" % median_sic
    results += "Average makespan: %.2f\n" % avg_makespan
    results += "Median makespan: %.2f\n" % median_makespan
    return results

if __name__ == "__main__":
    for agents in range(3,14):
        for tolerance in range(0,4):
            if tolerance == 0:
                genmap = True
                planner = "cbs"
            else:
                genmap = False
                planner = "tailcbs"
            results = test(agents, tolerance, planner, genmap)
            # Save results in file
            wa = "w" if tolerance==0 else "a"
            filename = "results/res_agents_" + str(agents)
            f = open(filename, wa)
            f.write(results)
            f.close()








