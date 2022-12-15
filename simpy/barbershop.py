from dataclasses import dataclass

import numpy
import generators

import constants
import statistics
from statistics import Statistics
from matplotlib.backends import backend_pdf
import entities
from scipy import stats
import math
import winsound

waiting_hall_fill = 0

blocked = False

#rqs = [0,0]

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
        yield env.timeout(generators.get_interval_before_new_customer_summer())



def switch_blocked_state_if_necessary():
    global blocked
    global waiting_hall_fill
    if (waiting_hall_fill >= constants.waiting_hall_max_fullness) and (not blocked):
        env.process(blocker(entities.cashbox_one, entities.unblock_event))
        env.process(blocker(entities.cashbox_two, entities.unblock_event))
    elif (waiting_hall_fill < constants.waiting_hall_max_fullness) and blocked:
        entities.unblock_event.succeed()
        entities.unblock_event = entities.env.event()

def blocker(resource, unblock_event):
    global blocked
    with resource.request(priority = constants.staff_priority_id) as req:
        yield req
        yield env.timeout(constants.time_of_switching_entrance)
        blocked = True
        yield (entities.env.timeout(constants.max_blocking_interval) | unblock_event)
        yield env.timeout(constants.time_of_switching_entrance)
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

def fix_arriving(resource):
    last_seen_input_time = statistics.get_last_seen_input_time(resource)
    if last_seen_input_time > 0:
        statistics.append_intensity_component(resource,1/(env.now - last_seen_input_time))
    statistics.set_last_seen_input_time(resource, env.now)

def fix_stop_serving(resource, start_serving_time):
    statistics.append_service_intensity_component(resource, 1/(entities.env.now - start_serving_time))

def customer(env, name, cashbox, services, review_desk, customer_priority):
    if constants.statistics_enable:
        fix_arriving(cashbox)
    try_print('%7.4f %s arrived' % (env.now, name))
    arriving_timestamp = env.now
    starting_serving_timestamp = env.now
    with cashbox.request(priority = customer_priority) as req:
        fix_entering_queue(cashbox, False)
        results = yield req | env.timeout(generators.get_waiting_interval())
        fix_leaving_queue(cashbox, False)
        if req in results:
            if constants.statistics_enable:
                statistics.append_waiting_time(cashbox, env.now - arriving_timestamp)
                handling_started = env.now
            yield env.timeout(generators.get_service_cashbox_interval())

            try_print('%7.4f %s served in cashbox' % (env.now, name))
            if constants.statistics_enable:
                statistics.append_presence_time(cashbox, env.now - arriving_timestamp)
                fix_stop_serving(cashbox, handling_started)
        else:
            try_print('%7.4f %s left without serving' % (env.now, name))
            statistics.increase_lost_quantity()
            return

    for service in services:
        if constants.statistics_enable:
            fix_arriving(service[0])
        arriving_timestamp = env.now
        try_print('%7.4f %s arrived at %s queue' % (arriving_timestamp, name, service[1]))
        fix_entering_queue(service[0], True)
        with service[0].request() as req:
            results = yield req
            if constants.statistics_enable:
                statistics.append_waiting_time(service[0], env.now - arriving_timestamp)
                handling_started = env.now
            fix_leaving_queue(service[0], True)
            yield env.timeout(service[2]())
            if constants.statistics_enable:
                statistics.append_presence_time(service[0], env.now - arriving_timestamp)
                fix_stop_serving(service[0], handling_started)
            try_print('%7.4f %s got %s' % (env.now, name, service[1]))

    with review_desk.request() as req:
        if constants.statistics_enable:
            fix_arriving(review_desk)
            arriving_timestamp = env.now
        results = yield req | env.timeout(0)

        if req in results:
            yield env.timeout(generators.get_writing_review_interval())
            if constants.statistics_enable:
                statistics.append_presence_time(review_desk, env.now - arriving_timestamp)
                fix_stop_serving(review_desk, arriving_timestamp)
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

def get_reliability_interval_relative_width(values):
    t_distribution = stats.t(len(values)-1)
    left_bound_of_reliability_interval = t_distribution.ppf(1-constants.student_parameter/2)

    mean = numpy.mean(criterias)
    reliability_interval = (left_bound_of_reliability_interval*numpy.std(values)/math.sqrt(len(criterias)))
    return reliability_interval/mean, mean, reliability_interval

def increase_index(index, maximum):
    index += 1
    if index < maximum:
        return index
    else:
        return 0

if (constants.find_optimal_number_of_clients):
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

            env = entities.env
            env.process(source(env, constants.number_of_clients))
            env.run()
            criteria = get_efficiency_criteria()
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
else:
    env = entities.env
    env.process(source(env, constants.number_of_clients))
    env.run()

@dataclass
class BarberShopStatistics():
    """ High level class for organizing gathered statistics into human readable
    format
    """
    def save_to_pdf(self, name: str) -> None:
        """Save all statistics for barber shop.

        :param name: Name of the pdf file to save. 
        """
        with backend_pdf.PdfPages(name) as pdf:
            _statistics = Statistics(pdf)
            _statistics.save_histogram_to_pdf(statistics.serving_times, 100,
                                  "Serving times", "length of serving (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(entities.cashbox_one), 50,
                                  "Waiting time in cashbox one queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(entities.cashbox_two), 10,
                                  "Waiting time in cashbox two queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(entities.short_hairing_hall), 50,
                                  "Waiting time in short hairing hall queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(entities.fashion_hairing_hall), 50,
                                  "Waiting time in fashion hairing hall queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(entities.colouring_hall), 50,
                                  "Waiting time in colouring hall queue", "length of waiting (minutes)", "quantity of clients")

            _statistics.save_histogram_to_pdf(statistics.get_presence_times(entities.cashbox_one), 50,
                                  "Presence time in cashbox one", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(entities.cashbox_two), 10,
                                  "Presence time in cashbox two", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(entities.short_hairing_hall), 50,
                                  "Presence time in short hairing hall", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(entities.fashion_hairing_hall), 50,
                                  "Presence time in fashion hairing hall", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(entities.colouring_hall), 50,
                                  "Presence time in colouring hall queue", "length of presence (minutes)", "quantity of clients")

    def log(self):
        """TODO: What it does, what's the purpose?
        """
        print("%f" % numpy.mean(statistics.get_queue_lengths(entities.cashbox_one)))
        print("%f" % numpy.mean(statistics.get_queue_lengths(entities.cashbox_two)))
        print("%f" % numpy.mean(statistics.get_queue_lengths(entities.short_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_queue_lengths(entities.fashion_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_queue_lengths(entities.colouring_hall)))

        print("%f" % numpy.mean(statistics.get_intensity_components(entities.cashbox_one)))
        print("%f" % numpy.mean(statistics.get_intensity_components(entities.cashbox_two)))
        print("%f" % numpy.mean(statistics.get_intensity_components(entities.short_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_intensity_components(entities.fashion_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_intensity_components(entities.colouring_hall)))
        print("%f" % numpy.mean(statistics.get_intensity_components(entities.review_desk)))

        print("%f" % numpy.mean(statistics.get_waiting_times(entities.cashbox_one)))
        print("%f" % numpy.mean(statistics.get_waiting_times(entities.cashbox_two)))
        print("%f" % numpy.mean(statistics.get_waiting_times(entities.short_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_waiting_times(entities.fashion_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_waiting_times(entities.colouring_hall)))

        print("%f" % numpy.mean(statistics.get_presence_times(entities.cashbox_one)))
        print("%f" % numpy.mean(statistics.get_presence_times(entities.cashbox_two)))
        print("%f" % numpy.mean(statistics.get_presence_times(entities.short_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_presence_times(entities.fashion_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_presence_times(entities.colouring_hall)))

        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.cashbox_one)))
        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.cashbox_two)))
        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.short_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.fashion_hairing_hall)))
        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.colouring_hall)))
        print("%f" % numpy.mean(statistics.get_service_intensity_components(entities.review_desk)))

        print("%f" % (statistics.lost_reviews/constants.number_of_clients))
        print("%f" % (statistics.lost/constants.number_of_clients))


if (constants.statistics_enable):
    barber_shop_statistics = BarberShopStatistics()
    barber_shop_statistics.save_to_pdf('barber_shop_statistics.pdf')
    # barber_shop_statistics.log()

#show_histogram(statistics.cashbox_queue_waiting_times[0], 100, "Cashbox one queue waiting times", "length of waiting (minutes)", "quantity of clients")
#show_histogram(statistics.cashbox_queue_waiting_times[1], 100, "Cashbox two queue waiting times", "length of waiting (minutes)", "quantity of clients")
