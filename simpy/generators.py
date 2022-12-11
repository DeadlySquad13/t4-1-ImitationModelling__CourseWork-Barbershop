import numpy
import constants

def get_class_id():
    num = numpy.random.rand()
    if (num < constants.short_hairing_client_probability):
        return constants.short_hairing_client_class_id
    if (num < constants.short_hairing_client_probability + constants.fashion_hairing_client_probability):
        return constants.fashion_hairing_client_class_id
    return constants.colouring_client_class_id

def get_random_priority():
    num = numpy.random.rand()
    if (num < constants.priority_client_probability):
        return constants.important_client_priority_id
    return constants.regular_client_priority_id

def get_interval_before_new_customer():
    return gamma(35,0.002,0.08,0.13)*60

def get_interval_before_new_customer_epidemic():
    return gamma(45,0.002,0.12,0.195)*60

def get_interval_before_new_customer_summer():
    return gamma(30,0.002,0.056,0.091)*60

def get_writing_review_interval():
    return gamma(4,0.7,3,5)

def get_waiting_after_colouring_interval():
    return gamma(40,0.8,25,40)

def get_service_colouring_interval():
    return gamma(12,0.8,5,15)

def get_service_fashion_hairing_interval():
    return gamma(12,5,40,90)

def get_service_short_hairing_interval():
    return gamma(22,0.85,20,25)

def get_service_cashbox_interval():
    return gamma(20,0.3,1,5)

def get_waiting_interval():
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