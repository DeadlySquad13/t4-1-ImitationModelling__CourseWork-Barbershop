# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 19:05:09 2017

@author: Zerbs

Modeling time: seconds
"""

import simpy

import generators



def barbershop(env):
    customers_in_system = 0
    
    queue_to_first_cashbox = 0
    queue_to_second_cashbox = 0
    
    while True:
        interval_before_new_customer = generators.get_interval_before_new_customer()
        customers_in_system += 1
        yield env.timeout(interval_before_new_customer)
        print("New customer at %d" % env.now)
        if (queue_to_first_cashbox < queue_to_second_cashbox):
            print("New customer is entered into first cashbox ")
            queue_to_first_cashbox += 1
            yield env.timeout(generators.get_interval_before_new_customer()*5)
            print("New customer left first cashbox ")
            queue_to_first_cashbox -= 1
        else:
            print("New customer is entered into second cashbox ")
            queue_to_second_cashbox += 1
            yield env.timeout(generators.get_interval_before_new_customer()*5)
            print("New customer left second cashbox ")
            queue_to_second_cashbox -= 1
        
if __name__ == "__main__":
    env = simpy.Environment()
    env.process(barbershop(env))
    env.run(300)