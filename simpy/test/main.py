# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 17:59:49 2017

@author: Zerbs

Modeling time in minutes
"""
import simpy
import matplotlib.pyplot as plt
import plotly.plotly as py

import generators

#def barbershop(env):
#    while True:
#        interval_before_new_customer = generators.get_interval_before_new_customer()
#        yield env.timeout(interval_before_new_customer)
#        print("New customer after %d" % interval_before_new_customer)
        
if __name__ == "__main__":
    #env = simpy.Environment()
    #env.process(barbershop(env))
    #env.run(300)
    print("ok")
    interval_before_new_customer = generators.get_interval_before_new_customer()
    #print(interval_before_new_customer)
    
    plt.hist(generators.get_number_set(22,0.85,20,25,1000),50)
    plt.title("Gamma Histogram")
    plt.xlabel("Quantity")
    plt.ylabel("Interval between customers")
    plt.grid(True)

    plt.show()
    #fig = plt.gcf()
    
    #py.sign_in("zeionara","0BvHagDSJMzgaRkmsspW")
    
    #plot_url = py.plot_mpl(fig, filename='mpl-basic-histogram')
    #print(plot_url)