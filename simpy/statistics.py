# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 15:50:46 2017

@author: Zerbs
"""
import matplotlib.pyplot as plt

def reset_statistics():
    global cashbox_queue_lengths
    global serving_times
    global cashbox_queue_length_sets
    global cashbox_queue_waiting_times

    global lost
    global lost_reviews

    global queue_lengths
    global waiting_times
    global queue_length

    global reviews_per_day_set

    global waiting_hall_fills

    global reviews_per_day

    global last_time_writing_reviews
    
    cashbox_queue_lengths = [0,0]
    serving_times = []
    cashbox_queue_length_sets =[[],[]]
    cashbox_queue_waiting_times =[[],[]]

    lost = 0
    lost_reviews = 0

    queue_lengths = {}
    waiting_times = {}
    queue_length = {}

    reviews_per_day_set = []

    waiting_hall_fills = []

    reviews_per_day = 0

    last_time_writing_reviews = 0


cashbox_queue_lengths = [0,0]
serving_times = []
cashbox_queue_length_sets =[[],[]]
cashbox_queue_waiting_times =[[],[]]

lost = 0
lost_reviews = 0

queue_lengths = {}
waiting_times = {}
queue_length = {}

reviews_per_day_set = []

waiting_hall_fills = []

reviews_per_day = 0
day_length = 480

last_time_writing_reviews = 0



def get_queue_length(resource):
    try:
        return queue_length[resource]
    except:
        queue_length[resource] = 0
        return queue_length[resource]

def increase_queue_length(resource):
    try:
        queue_length[resource] += 1
    except:
        queue_length[resource] = 1
        
def decrease_queue_length(resource):
    try:
        queue_length[resource] -= 1
    except:
        queue_length[resource] = 0

def append_queue_length(resource):
    if (queue_length == 0):
        return
    append_value_to_collection(resource, queue_lengths, queue_length[resource])
        
def get_queue_lengths(resource):
    return get_values_from_collection(resource, queue_lengths)
    
def append_waiting_time(resource, time):
    if (time == 0):
        return
    append_value_to_collection(resource, waiting_times, time)
        
def get_waiting_times(resource):
    return get_values_from_collection(resource, waiting_times)
    
def append_value_to_collection(resource, collection, value):
    try:
        collection[resource].append(value)
    except:
        collection[resource] = []
        collection[resource].append(value)
        
def get_values_from_collection(resource, collection):
    try:
        return collection[resource]
    except:
        return [0]

def show_histogram(collection, number_of_intervals, title, xlabel, ylabel):
    plt.hist(collection,number_of_intervals)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()
    
def increase_lost_quantity():
    global lost
    lost += 1
    
def increase_lost_reviews_quantity():
    global lost_reviews
    lost_reviews += 1