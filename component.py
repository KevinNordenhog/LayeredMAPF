

#returns the list of agents (the component) in the agents component
def getComponent(schedule, agent, start):
    component = [agent]
    positions = []
    positions += schedule[agent]
    finished = False

    while not finished:
        finished = True
        for a in schedule:
            if a in component:
                continue
            for i in range(start, len(schedule[a])):
                if schedule[a][i] in positions:
                    finished = False
                    positions += schedule[a]
                    component.append(a)
                    break

    return component


# The length of the longest path in schedule
def makespan(solution):
    return len(solution[max(solution, key = lambda x: len(solution[x]))])
    

def getBoundedComponent(schedule, agent, start, bound):
    make = makespan(schedule)
    component = [agent]

    finished = False
    while not finished:
        finished = True
        for t in range(start, make):
            positions = {}
            for c in component:
                for i in range(t, t+bound+1):
                    if i >= len(schedule[c]):
                        i = -1#len(schedule[c])-1
                    positions[schedule[c][i]] = [[c, i]]
            # The position of each agent and their tails at time t
            for other_agent in schedule:
                if other_agent == agent:
                    continue
                addPos(positions, schedule, other_agent, t, bound)
            for pos, agents in positions.items():
                if len(agents) > 1:
                    for a,_ in agents:
                        if a in component:
                            continue
                        else:
                            finished = False
                            component.append(a)
                    
    return component

# Set the current position of an agent and its tail
def addPos(positions,  schedule, agent, t, bound):
    for k in range(0, bound+1):
        time = t+k
        pos = t+k
        if time < 0: # Check for negative time
            continue
        if time >= len(schedule[agent]):
            time = t
            pos = len(schedule[agent])-1
        if schedule[agent][pos] in positions:
            c = [x for x,_ in positions[schedule[agent][pos]]] # agent
            n = [x for _,x in positions[schedule[agent][pos]]] # time
            # Update the time of the agent if it is in list already
            # (only save the latest time on that position)
            if agent in c: #
                i = c.index(agent)
                if time > n[i]:
                    positions[schedule[agent][pos]][i][1] = time
            # If agent is not in list, add it
            else:
                positions[schedule[agent][pos]].append([agent, time])
