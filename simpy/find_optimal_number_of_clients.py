import numpy

import constants
import statistics
import simulation
from scipy import stats
import math
import winsound

waiting_hall_fill = 0

blocked = False

# Change with `range`? Change with `max`?
def increase_index(index, maximum):
    index += 1
    if index < maximum:
        return index
    else:
        return 0

def reset():
    global waiting_hall_fill
    global blocked

    statistics.reset_statistics()
    waiting_hall_fill = 0
    blocked = False

def get_efficiency_criteria(cashbox_one, cashbox_two):
    return (numpy.mean(statistics.reviews_per_day_set) -
      (constants.short_hairing_masters_quantity +
       constants.fashion_hairing_masters_quantity +
       constants.colouring_masters_quantity) -
       numpy.mean(statistics.waiting_hall_fills) -
       (numpy.mean(statistics.get_queue_lengths(cashbox_one)) +
        numpy.mean(statistics.get_queue_lengths(cashbox_two))))

def get_reliability_interval_relative_width(values):
    t_distribution = stats.t(len(values)-1)
    left_bound_of_reliability_interval = t_distribution.ppf(1-constants.student_parameter/2)

    mean = numpy.mean(values)
    reliability_interval = (left_bound_of_reliability_interval*numpy.std(values)/math.sqrt(len(values)))
    return reliability_interval/mean, mean, reliability_interval

def find_optimal_number_of_clients():
    """{Incrementally decreases interval width ?}

    :param self: 
    :type self: 
    """
    previous_means = []
    previous_means_index = 0
    print("%20s | %20s | %22s" % ("number of clients","interval width (%)",
                                  "efficiency criterion"))
    print("-"*68)
    counter = 1
    accuracy = 1
    prev_accuracy = 1
    prev_prev_accuracy = 1
    general_accuracy = 1
    general_interval_width = 1
    general_mean = 1
    common_accuracy = 1
    common_prev_accuracy = 1
    common_prev_prev_accuracy = 1
    while (counter < constants.number_of_considered_means) or \
            (common_accuracy > constants.minimal_accuracy) or \
            (common_prev_accuracy > constants.minimal_accuracy) or \
            (common_prev_prev_accuracy > constants.minimal_accuracy):

        prev_prev_accuracy = prev_accuracy
        prev_accuracy = accuracy

        common_prev_prev_accuracy = common_prev_accuracy
        common_prev_accuracy = common_accuracy
        criterias = []
        for i in range(5):
            sim = simulation.Simulation()

            # env = entities.env
            # env.process(utils.source(env, constants.number_of_clients))
            # env.run()
            criteria = get_efficiency_criteria(sim.entities.cashbox_one,
                                               sim.entities.cashbox_two)
            criterias.append(criteria)
            reset()

        accuracy, mean, interval_width = get_reliability_interval_relative_width(criterias)
        #print("-")

        if counter <= constants.number_of_considered_means:
            previous_means.append(mean)
            print("-")
        else:
            previous_means[previous_means_index] = mean
            previous_means_index = increase_index(previous_means_index, constants.number_of_considered_means)
            general_accuracy, general_mean, general_interval_width = get_reliability_interval_relative_width(previous_means)
            common_accuracy = (general_interval_width+interval_width)/general_mean
            print("%20i | %20.4f | %22s" % (constants.number_of_clients, common_accuracy*100,
                                        "%7.4f ± %7.4f" % (general_mean,general_interval_width+interval_width)))
        if (common_accuracy > constants.minimal_accuracy):
            winsound.Beep(500, 1000)
        else:
            winsound.Beep(2500, 1000)
        constants.number_of_clients += constants.step_number_of_clients
        counter += 1
    print("Optimal number of clients is %i" % (constants.number_of_clients - constants.step_number_of_clients*3))

find_optimal_number_of_clients()
