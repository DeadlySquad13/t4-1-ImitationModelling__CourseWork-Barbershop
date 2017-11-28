# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 19:58:52 2017

@author: Zerbs
"""
import simpy
import numpy
import generators
import matplotlib.pyplot as plt
import constants
import statistics
import entities
from scipy import stats
import math

waiting_hall_fill = 0

blocked = False

rqs = [0,0]



def get_services(customer_class):
    services = []
    if (customer_class == 1):
        services.append((entities.short_hairing_hall, " short hairdressing ", generators.get_service_short_hairing_interval))
    elif (customer_class == 2):
        services.append((entities.fashion_hairing_hall, " fashion hairdressing ", generators.get_service_fashion_hairing_interval))
    else:
        services.append((entities.colouring_hall, " colouring ", generators.get_service_colouring_interval))
        services.append((entities.waiting_after_colouring, " waiting after colouring ", generators.get_waiting_after_colouring_interval))
        services.append((entities.colouring_hall, " drying ", generators.get_service_colouring_interval))
    return services

def get_cashbox():
    if (statistics.get_queue_length(entities.cashbox_two) < statistics.get_queue_length(entities.cashbox_one)):
        return entities.cashbox_two
    return entities.cashbox_one

def source(env, quantity):
    global waiting_hall_fill
    global blocked
    global rqs
    for i in range(quantity): 
        c = customer(env, 
                     'Customer%02d' % i, 
                     get_cashbox(), 
                     get_services(generators.get_class_id()), 
                     entities.review_desk, 
                     generators.get_random_priority())

        env.process(c)
        yield env.timeout(generators.get_interval_before_new_customer())
    
    

def switch_blocked_state_if_necessary():
    global blocked
    global waiting_hall_fill
    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>%i" % waiting_hall_fill)
    #print(blocked)
    if (waiting_hall_fill >= constants.waiting_hall_max_fullness) and (not blocked):
        env.process(blocker(entities.cashbox_one, entities.unblock_event))
        env.process(blocker(entities.cashbox_two, entities.unblock_event))
        #blocked = True
    elif (waiting_hall_fill < constants.waiting_hall_max_fullness) and blocked:
        #print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,%i" % waiting_hall_fill)
        entities.unblock_event.succeed()
        entities.unblock_event = entities.env.event()
        #blocked = False
        
def blocker(resource, unblock_event):
    global blocked
    with resource.request(priority = constants.staff_priority_id) as req:
        yield req
        yield entities.env.timeout(100)
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>BLOCKED")
        blocked = True
        yield entities.env.timeout(constants.max_blocking_interval) | unblock_event
        yield entities.env.timeout(100)
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>UNBLOCKED")
        blocked = False
        
def try_print(message):
    if constants.verbous:
        print(message)

def increase_waiting_hall_fullness():
    global waiting_hall_fill
    statistics.waiting_hall_fills.append(waiting_hall_fill)
    waiting_hall_fill += 1
    
def decrease_waiting_hall_fullness():
    global waiting_hall_fill
    statistics.waiting_hall_fills.append(waiting_hall_fill)
    waiting_hall_fill -= 1

def fix_entering_queue(resource, is_it_waiting_hall):
    statistics.increase_queue_length(resource)
    statistics.append_queue_length(resource)
    if (is_it_waiting_hall):
        increase_waiting_hall_fullness()
        switch_blocked_state_if_necessary()

def fix_leaving_queue(resource, is_it_waiting_hall):
    statistics.decrease_queue_length(resource)
    #print(statistics.get_queue_length(resource))
    statistics.append_queue_length(resource)
    if (is_it_waiting_hall):
        decrease_waiting_hall_fullness()
        switch_blocked_state_if_necessary()

def update_reviews_per_day():
    statistics.reviews_per_day += 1
    if entities.env.now - statistics.last_time_writing_reviews >= statistics.day_length:
        statistics.reviews_per_day_set.append(statistics.reviews_per_day)
        statistics.reviews_per_day = 0
        statistics.last_time_writing_reviews = entities.env.now

def customer(env, name, cashbox, services, review_desk, customer_priority):
    try_print('%7.4f %s arrived' % (env.now, name))
    arriving_timestamp = env.now
    starting_serving_timestamp = env.now
    with cashbox.request(priority = customer_priority) as req:       
        fix_entering_queue(cashbox, False)
        results = yield req | env.timeout(generators.get_waiting_interval())
        fix_leaving_queue(cashbox, False)
        if req in results:
            statistics.append_waiting_time(cashbox, env.now - arriving_timestamp)
            yield env.timeout(generators.get_service_cashbox_interval())
            try_print('%7.4f %s served in cashbox' % (env.now, name))
        else:
            try_print('%7.4f %s left without serving' % (env.now, name))
            statistics.increase_lost_quantity()
            return
    
    for service in services:
        arriving_timestamp = env.now
        try_print('%7.4f %s arrived at %s queue' % (arriving_timestamp, name, service[1]))
        fix_entering_queue(service[0], True)
        with service[0].request() as req:
            results = yield req
            statistics.append_waiting_time(service[0], env.now - arriving_timestamp)
            #
            fix_leaving_queue(service[0], True)
            yield env.timeout(service[2]())
            try_print('%7.4f %s got %s' % (env.now, name, service[1]))
    
    with review_desk.request() as req:
            results = yield req | env.timeout(0)
            
            if req in results:
                yield env.timeout(generators.get_writing_review_interval())
                update_reviews_per_day()
            else:
                statistics.increase_lost_reviews_quantity()
    
    try_print('%7.4f %s successfully served' % (env.now, name))
    statistics.serving_times.append(env.now - starting_serving_timestamp)
    return

def reset():
    global waiting_hall_fill
    global blocked
    
    statistics.reset_statistics()
    waiting_hall_fill = 0
    blocked = False

def get_efficiency_criteria():
    return (numpy.mean(statistics.reviews_per_day_set) - 
      (constants.short_hairing_masters_quantity +
       constants.fashion_hairing_masters_quantity + 
       constants.colouring_masters_quantity) -
       numpy.mean(statistics.waiting_hall_fills) -
       (numpy.mean(statistics.get_queue_lengths(entities.cashbox_one)) + 
        numpy.mean(statistics.get_queue_lengths(entities.cashbox_two))))

# Setup and start the simulation
criterias = []
occuracity = 1
while (occuracity > 0.05):
    for i in range(5):
        
        env = entities.env
    
        env.process(source(env, constants.number_of_clients))
        env.run()
        #print(numpy.mean(statistics.waiting_hall_fills))
        criteria = get_efficiency_criteria()
        criterias.append(criteria)
        
        reset()
    #print(criterias)
    
    alfa=0.05              # уровень значимости
    n=len(criterias)-1            # число степеней свободы
    t=stats.t(n)
    tcr=t.ppf(1-alfa/2)
    
    mean = numpy.mean(criterias)
    dis = (tcr*numpy.std(criterias)/math.sqrt(len(criterias)))
    occuracity = dis/mean
    
    #print("mean = %f" % mean)
    #print("disp = %f" % dis)
    print("for %i clients width of reliability interval is %f %%" % (constants.number_of_clients, occuracity*100))
    constants.number_of_clients *= 2
    
print("Optimal number of clients is %i" % constants.number_of_clients)
    

#print("Losing probability = %f" % (statistics.lost/1000))
#print(statistics.get_waiting_times(entities.cashbox_one))

if (constants.statistics_enable):
    statistics.show_histogram(statistics.serving_times, 100, 
                          "Serving times", "length of serving (minutes)", "quantity of clients")
    statistics.show_histogram(statistics.get_waiting_times(entities.cashbox_one), 100, 
                          "Waiting time in cashbox one queue", "length of waiting (minutes)", "quantity of clients")
    statistics.show_histogram(statistics.get_waiting_times(entities.cashbox_two), 100, 
                          "Waiting time in cashbox two queue", "length of waiting (minutes)", "quantity of clients")
    statistics.show_histogram(statistics.get_waiting_times(entities.short_hairing_hall), 100, 
                          "Waiting time in short hairing hall queue", "length of waiting (minutes)", "quantity of clients")
    statistics.show_histogram(statistics.get_waiting_times(entities.fashion_hairing_hall), 100, 
                          "Waiting time in fashion hairing hall queue", "length of waiting (minutes)", "quantity of clients")
    statistics.show_histogram(statistics.get_waiting_times(entities.colouring_hall), 100, 
                          "Waiting time in colouring hall queue", "length of waiting (minutes)", "quantity of clients")
    print("Average cashbox one queue length = %f" % numpy.mean(statistics.get_queue_lengths(entities.cashbox_one)))
    print("Average cashbox two queue length = %f" % numpy.mean(statistics.get_queue_lengths(entities.cashbox_two)))
    print("Average short hairing queue length = %f" % numpy.mean(statistics.get_queue_lengths(entities.short_hairing_hall)))
    print("Average cashbox two queue length = %f" % numpy.mean(statistics.get_queue_lengths(entities.cashbox_two)))
    print("Losing review probability = %f" % (statistics.lost_reviews/constants.number_of_clients))
    print("Losing probability = %f" % (statistics.lost/constants.number_of_clients))
#show_histogram(statistics.cashbox_queue_waiting_times[0], 100, "Cashbox one queue waiting times", "length of waiting (minutes)", "quantity of clients")
#show_histogram(statistics.cashbox_queue_waiting_times[1], 100, "Cashbox two queue waiting times", "length of waiting (minutes)", "quantity of clients")