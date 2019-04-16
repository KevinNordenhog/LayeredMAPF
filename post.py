import sys

def post(schedule):
    windows = []
    count = {}
    #loops from 0 to the length of the longest paths
    for i in range(0, len(schedule[max(schedule, key = lambda x: len(schedule[x]))])):
        stops = []
        for agent in schedule:
            if len(schedule[agent]) > i:
                if schedule[agent][i] in count:
                    if not count[schedule[agent][i]][0] == agent:
                        windows.append(count[schedule[agent][i]][1])
                        count[schedule[agent][i]] = [agent, 0]
                        stops.append(schedule[agent][i])
                else:
                    count[schedule[agent][i]] = [agent, 0]

        for pos in count:
            if not pos in stops:
                count[pos][1] += 1
    if windows:
        return min(windows)
    else:
        return sys.maxsize
