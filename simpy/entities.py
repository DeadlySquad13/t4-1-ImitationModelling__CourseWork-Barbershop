import simpy
import constants

env = simpy.Environment()

#devices
unblock_event = env.event()
cashbox_one = simpy.PriorityResource(env, capacity=1)
cashbox_two = simpy.PriorityResource(env, capacity=1)

short_hairing_hall = simpy.Resource(env, capacity=constants.short_hairing_masters_quantity)
fashion_hairing_hall = simpy.Resource(env, capacity=constants.fashion_hairing_masters_quantity)
colouring_hall = simpy.Resource(env, capacity=constants.colouring_masters_quantity)
waiting_after_colouring = simpy.Resource(env, capacity=constants.waiting_hall_max_fullness*2)

review_desk = simpy.Resource(env, capacity=1)
