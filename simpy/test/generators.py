# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 18:04:59 2017

@author: Zerbs
"""
import numpy

def get_interval_before_new_customer():
    return gamma(45,0.002,0.08,0.13)*60
    #numbers = []
    #for i in range(5000):
    #    numbers.append(gamma(60,0.1,4.8,8))
    #return numbers 

part_short_hairing = 0.3
part_fashion_hairing = 0.45

def get_class_id():
    num = numpy.random.rand()
    if (num < part_short_hairing):
        return 1
    if (num < part_short_hairing + part_fashion_hairing):
        return 2
    return 3

def get_random_priority():
    num = numpy.random.rand()
    if (num < 0.28):
        return 1
    return 2

def get_writing_review_interval():
    return gamma(4,0.7,3,5)

def get_waiting_after_colouring_interval():
    return gamma(35,0.8,25,40)

def get_service_colouring_interval():
    return gamma(9,0.8,5,15)

def get_service_fashion_hairing_interval():
    return gamma(9,5,40,90)

def get_service_short_hairing_interval():
    return gamma(22,0.85,20,25)

def get_service_cashbox_interval():
    return gamma(7,0.3,1,5)

def get_waiting_interval():
    return empirical()

def get_number_set(shape, scale, min, max, quantity):
    #return gamma(60, 0.1, 4.8, 8)
    numbers = []
    for i in range(quantity):
        numbers.append(gamma(shape, scale, min, max))
        #numbers.append(empirical())
        #numbers.append(get_class_id())
    return numbers 

def empirical():
    k = 0.033
    num = numpy.random.rand()
    if num <= k * 1:
        return gamma(2, 5, 1, 2)
    elif num <= k * 3:
        return gamma(2, 5, 2, 3)
    elif num <= k * 6:
        return gamma(2, 5, 3, 4)
    elif num <= k * 10:
        return gamma(2, 5, 4, 4.9)
    elif num <= k * 20:
        return gamma(2, 5, 4.9, 5.1)
    elif num <= k * 24:
        return gamma(2, 5, 5.1, 6)
    elif num <= k * 27:
        return gamma(2, 5, 6, 7)
    elif num <= k * 29:
        return gamma(2, 5, 7, 9)
    else:
        return gamma(2, 5, 9, 10)
    return num

def gamma(shape, size, min, max):
    result = numpy.random.gamma(shape,size)
    while (result < min) or (result > max):
        result = numpy.random.gamma(shape,size)
    return result