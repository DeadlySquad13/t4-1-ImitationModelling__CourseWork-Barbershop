import simpy
import constants

env = simpy.Environment()

class Entities():
    def __init__(self, env: simpy.Environment) -> None:
        self.unblock_event = env.event()

        self.cashbox_one = simpy.PriorityResource(env, capacity=1)
        self.cashbox_two = simpy.PriorityResource(env, capacity=1)

        self.short_hairing_hall = simpy.Resource(env, capacity=constants.short_hairing_masters_quantity)
        self.fashion_hairing_hall = simpy.Resource(env, capacity=constants.fashion_hairing_masters_quantity)
        self.colouring_hall = simpy.Resource(env, capacity=constants.colouring_masters_quantity)
        self.waiting_after_colouring = simpy.Resource(env, capacity=constants.waiting_hall_max_fullness*2)

        self.review_desk = simpy.Resource(env, capacity=1)

