from dataclasses import dataclass
import simpy
from entities import Entities

import generators

import constants
import statistics

@dataclass
class Simulation:
    env = simpy.Environment()
    entities = Entities(env)
    waiting_hall_fill = 0
    blocked = False

    def __post_init__(self) -> None:
        # Run simulation.
        self.env.process(self.source(constants.number_of_clients))
        self.env.run()


    def switch_blocked_state_if_necessary(self):
        if (self.waiting_hall_fill >= constants.waiting_hall_max_fullness) and (not self.blocked):
            self.env.process(self.blocker(self.entities.cashbox_one, self.entities.unblock_event))
            self.env.process(self.blocker(self.entities.cashbox_two, self.entities.unblock_event))
        elif (self.waiting_hall_fill < constants.waiting_hall_max_fullness) and self.blocked:
            self.entities.unblock_event.succeed()
            self.entities.unblock_event = self.env.event()

    def blocker(self, resource, unblock_event):
        with resource.request(priority = constants.staff_priority_id) as req:
            yield req
            yield self.env.timeout(constants.time_of_switching_entrance)
            self.blocked = True
            yield (self.env.timeout(constants.max_blocking_interval) | unblock_event)
            yield self.env.timeout(constants.time_of_switching_entrance)
            self.blocked = False

    def try_print(self, message):
        if constants.verbose:
            print(message)

    def increase_waiting_hall_fullness(self):
        statistics.waiting_hall_fills.append(self.waiting_hall_fill)
        self.waiting_hall_fill += 1

    def decrease_waiting_hall_fullness(self):
        statistics.waiting_hall_fills.append(self.waiting_hall_fill)
        self.waiting_hall_fill -= 1


    def fix_entering_queue(self, resource, is_it_waiting_hall):
        statistics.increase_queue_length(resource)
        statistics.append_queue_length(resource)
        if (is_it_waiting_hall):
            self.increase_waiting_hall_fullness()
            self.switch_blocked_state_if_necessary()

    def fix_leaving_queue(self, resource, is_it_waiting_hall):
        statistics.decrease_queue_length(resource)
        statistics.append_queue_length(resource)
        if (is_it_waiting_hall):
            self.decrease_waiting_hall_fullness()
            self.switch_blocked_state_if_necessary()

    def update_reviews_per_day(self):
        statistics.reviews_per_day += 1
        if self.env.now - statistics.last_time_writing_reviews >= statistics.day_length:
            statistics.reviews_per_day_set.append(statistics.reviews_per_day)
            statistics.reviews_per_day = 0
            statistics.last_time_writing_reviews = self.env.now

    def fix_arriving(self, resource):
        last_seen_input_time = statistics.get_last_seen_input_time(resource)
        if last_seen_input_time > 0:
            statistics.append_intensity_component(resource,1/(self.env.now - last_seen_input_time))
        statistics.set_last_seen_input_time(resource, self.env.now)

    def fix_stop_serving(self, resource, start_serving_time):
        statistics.append_service_intensity_component(resource, 1/(self.env.now - start_serving_time))

    def customer(self, env, name, cashbox, services, review_desk, customer_priority):
        if constants.statistics_enable:
            self.fix_arriving(cashbox)
        self.try_print('%7.4f %s arrived' % (env.now, name))
        arriving_timestamp = env.now
        starting_serving_timestamp = env.now
        with cashbox.request(priority = customer_priority) as req:
            self.fix_entering_queue(cashbox, False)
            results = yield req | env.timeout(generators.get_waiting_interval())
            self.fix_leaving_queue(cashbox, False)
            if req in results:
                if constants.statistics_enable:
                    statistics.append_waiting_time(cashbox, env.now - arriving_timestamp)
                    handling_started = env.now
                yield env.timeout(generators.get_service_cashbox_interval())

                self.try_print('%7.4f %s served in cashbox' % (env.now, name))
                if constants.statistics_enable:
                    statistics.append_presence_time(cashbox, env.now - arriving_timestamp)
                    self.fix_stop_serving(cashbox, handling_started)
            else:
                self.try_print('%7.4f %s left without serving' % (env.now, name))
                statistics.increase_lost_quantity()
                return

        for service in services:
            if constants.statistics_enable:
                self.fix_arriving(service[0])
            arriving_timestamp = env.now
            self.try_print('%7.4f %s arrived at %s queue' % (arriving_timestamp, name, service[1]))
            self.fix_entering_queue(service[0], True)
            with service[0].request() as req:
                results = yield req
                if constants.statistics_enable:
                    statistics.append_waiting_time(service[0], env.now - arriving_timestamp)
                    handling_started = env.now
                self.fix_leaving_queue(service[0], True)
                yield env.timeout(service[2]())
                if constants.statistics_enable:
                    statistics.append_presence_time(service[0], env.now - arriving_timestamp)
                    self.fix_stop_serving(service[0], handling_started)
                self.try_print('%7.4f %s got %s' % (env.now, name, service[1]))

        with review_desk.request() as req:
            if constants.statistics_enable:
                self.fix_arriving(review_desk)
                arriving_timestamp = env.now
            results = yield req | env.timeout(0)

            if req in results:
                yield env.timeout(generators.get_writing_review_interval())
                if constants.statistics_enable:
                    statistics.append_presence_time(review_desk, env.now - arriving_timestamp)
                    self.fix_stop_serving(review_desk, arriving_timestamp)
                self.update_reviews_per_day()
            else:
                statistics.increase_lost_reviews_quantity()

        self.try_print('%7.4f %s successfully served' % (env.now, name))
        statistics.serving_times.append(env.now - starting_serving_timestamp)
        return


    def get_services(self, customer_class):
        services = []
        if (customer_class == 1):
            services.append((self.entities.short_hairing_hall, " short hairdressing ", generators.get_service_short_hairing_interval))
        elif (customer_class == 2):
            services.append((self.entities.fashion_hairing_hall, " fashion hairdressing ", generators.get_service_fashion_hairing_interval))
        else:
            services.append((self.entities.colouring_hall, " colouring ", generators.get_service_colouring_interval))
            services.append((self.entities.waiting_after_colouring, " waiting after colouring ", generators.get_waiting_after_colouring_interval))
            services.append((self.entities.colouring_hall, " drying ", generators.get_service_colouring_interval))
        return services

    def get_cashbox(self):
        if (statistics.get_queue_length(self.entities.cashbox_two) <
            statistics.get_queue_length(self.entities.cashbox_one)):
            return self.entities.cashbox_two
        return self.entities.cashbox_one


    def source(self, quantity):
        global rqs
        for i in range(quantity):
            c = self.customer(self.env,
                         'Customer%02d' % i,
                         self.get_cashbox(),
                         self.get_services(generators.get_class_id()),
                         self.entities.review_desk,
                         generators.get_random_priority())

            self.env.process(c)
            yield self.env.timeout(generators.get_interval_before_new_customer_summer())

