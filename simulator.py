#!/usr/bin/env python3
import yaml
import matplotlib
import agent
import map


class Simulator:
    def __init__(self):
        
    
        map = Map(filename) #[[object, object],[]] 
        agents = creatagents(filename)  #dict
        schedule = Global(map, agents)  # dict (agent:  [path])




        #matplotlib function that repeatedly calles a function func, frames is the parameter(s)
        self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                               init_func=self.init_func,
                               frames=int(self.T+1) * 10,
                               interval=100,
                               blit=True)

    def creatagents(self, filename):
        # for agent in filename:
        #     agent = Agent()


if __name__=="__main__":
    return


    