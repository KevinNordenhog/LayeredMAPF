import generatemap
import simulator
import yaml
import time
import signal
import sys
import math
import os


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
    test_no = 10
    size = "warehouse" # "n" or "warehouse"
    density = 0
    path_map = "results/agents_%d/maps" % agents
    delay_toggle = True
    prob_delay = 5
    animate = False
    # Generate map
    if genmap:
        if not os.path.isdir(path_map):
            os.mkdir(path_map)
        for i in range(test_no):
            map_config = generatemap.gen_map(size, density, agents, 0, 0)
            generatemap.save_map(map_config, path_map + "/map%d.yaml" % i)
            world = yaml.load(map_config)
    # Create directory where schedules are saved
    if global_planner == "cbs":
        path_schedule = "results/agents_%d/schedule_%s" % (agents,global_planner)
    else:
        s = "cbs-t%d" % delay_tolerance
        path_schedule = "results/agents_%d/schedule_%s" % (agents,s)
    if not os.path.isdir(path_schedule):
        os.mkdir(path_schedule)
    # Keep track of test results 
    start = time.time()
    runtime = []
    nodes = []
    sic = []
    makespan = []
    # Local planner data
    dev_count = []
    tot_dev = []
    local_runtime = []
    total_makespan = []
    total_sic = []
    stalls = []
    recalculations = []

    failed_tests = 0
    # Run and evaluate algorithm on 100 maps
    for i in range(test_no):
        # Load map
        with open(path_map + "/map%d.yaml" % i) as map_file:
            world = yaml.load(map_file)
        # Count time and stop tests that exceed 5 minutes
        t = time.time()
        test_no += 1
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(300)
        # Path finding
        try:
            print ("\nRunning test %d" % i)
            sim = simulator.Simulator(world, global_planner, delay_tolerance)
            sim.simulate(delay_toggle, animate, prob_delay)
            # Save runtime data
            nodes += [sim.planner.node_cnt]
            sic += [sim.planner.cost]
            makespan += [sim.planner.makespan]
            r_time = time.time()-t
            runtime += [r_time]
            # Local planner data
            dev_count += [sim.planner.deviation_count]
            tot_dev += [sim.planner.tot_deviations]
            local_runtime += sim.planner.time_local #this already is a list of times
            total_makespan += [sim.planner.tot_makespan]
            total_sic += [sim.planner.tot_sic]
            stalls += [sim.planner.no_stalls]
            recalculations += [sim.planner.no_recalc]
            # Save schedule and test statistics
            f = open(path_schedule+"/test_%d"%i, "w")
            schedule = ""
            for a, s in sim.planner.schedule.items():
                schedule += "%s: %s\n" % (a,s)
            data = ("Schedule:\n %s\n\n" % schedule
                    + "Nodes: %d\n" % sim.planner.node_cnt
                    + "SIC: %d\n" % sim.planner.cost
                    + "Makespan: %d\n" % sim.planner.makespan
                    + "Run-time: %.6f\n" % r_time)
            f.write(data)
            f.close()
        except Timeout:
            failed_tests += 1
            print("Took too long (>5 minutes)")

    # Special case when all tests run for over 5min
    if failed_tests == 100:
        print ("\n Test passed with 0% success rate")
        return "Succes rate: 0%"

    # Test has finished
    tot_time = time.time()-start
    print ("\nTest finished.")
    print ("Total time: %.6f" % tot_time)
    print ("Success rate: %d%%" % (100-failed_tests))
    # Overview of all 100 instances
    nodes = sorted(nodes)
    sic = sorted(sic)
    makespan = sorted(makespan)
    runtime = sorted(runtime)
    avg_nodes = sum(nodes)/len(nodes)
    avg_runtime = sum(runtime)/len(runtime)
    avg_sic = sum(sic)/len(sic)
    avg_makespan = sum(makespan)/len(makespan)
    median_nodes = nodes[int(len(nodes)/2)]
    median_runtime = runtime[int(len(runtime)/2)]
    median_sic = sic[int(len(sic)/2)]
    median_makespan = makespan[int(len(makespan)/2)]
    # Return a formated overview
    results = "\n"
    results += "Global\n"
    results += "Tolerance: %d\n" % delay_tolerance
    results += "Total time: %.6f\n" % tot_time
    results += "Success rate: %d%%\n" % (100-failed_tests)
    results += "Average run-time: %.6f\n" % avg_runtime
    results += "Median run-time: %.6f\n" % median_runtime
    results += "Variance (runtime): %.6f\n" % variance(runtime)
    results += "Average generated nodes: %d\n" % avg_nodes
    results += "Median generated nodes: %d\n" % median_nodes
    results += "Average sic: %.2f\n" % avg_sic
    results += "Median sic: %.2f\n" % median_sic
    results += "Average makespan: %.2f\n" % avg_makespan
    results += "Median makespan: %.2f\n" % median_makespan

    #Local
    dev_count = sorted(dev_count)
    tot_dev = sorted(tot_dev)
    local_runtime = sorted(local_runtime)
    total_makespan = sorted(total_makespan)
    total_sic =sorted(total_sic)
    stalls = sorted(stalls)
    recalculations = sorted(recalculations)

    avg_dev_count = sum(dev_count)/len(dev_count)
    avg_tot_dev = sum(tot_dev)/len(tot_dev)
    avg_total_makespan = sum(total_makespan)/len(total_makespan)
    avg_total_sic = sum(total_sic)/len(total_sic)
    avg_stalls = sum(stalls)/len(stalls)
    #Avoid division by zero
    if (len(local_runtime)):
        avg_local_runtime = sum(local_runtime)/len(local_runtime)
    else:
        avg_local_runtime = 0
    #Avoid division by zero
    if (len(recalculations)):
        avg_recalculations = sum(recalculations)/len(recalculations)
    else:
        avg_recalculations = 0

    
    results += "\n"
    results += "Local\n"
    results += "Average number of unique deviations: %.2f\n" % avg_dev_count 
    results += "Average number of deviations: %.2f\n" % avg_tot_dev
    results += "Average runtime of local planner: %.6f\n" % avg_local_runtime
    results += "Average makespan after execution: %.2f\n" % avg_total_makespan
    results += "Average SIC after execution: %.2f\n" % avg_total_sic
    results += "Average number of stalls: %.2f\n" % avg_stalls
    results += "Average number of recalculations: %.2f\n" % avg_recalculations
    results += "--------------------------\n"
    
    return results

if __name__ == "__main__":
    agents_min = 3
    agents_max = 8
    tolerance_min = 0
    tolerance_max = 3
    for agents in range(agents_min, agents_max+1):
        for tolerance in range(tolerance_min, tolerance_max+1):
            if tolerance == 0:
                genmap = True
                planner = "cbs"
            else:
                genmap = False
                planner = "tailcbs"
            # Log data here
            path = "results/agents_%d" % agents
            if not os.path.isdir(path):
                os.mkdir(path)
            # Run test
            results = test(agents, tolerance, planner, genmap)
            # Save overview of results in file
            wa = "w" if tolerance==0 else "a"
            filename = "results/agents_%d/overview" % agents
            f = open(filename, wa)
            f.write(results)
            f.close()








