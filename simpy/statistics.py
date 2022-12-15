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
    global presence_times
    global intensity_components
    global service_intensity_components
    global figures_counter
    
    cashbox_queue_lengths = [0,0]
    serving_times = []
    cashbox_queue_length_sets =[[],[]]
    cashbox_queue_waiting_times =[[],[]]
    figures_counter = 0
    lost = 0
    lost_reviews = 0

    queue_lengths = {}
    waiting_times = {}
    queue_length = {}
    presence_times = {}
    intensity_components = {}
    service_intensity_components = {}

    reviews_per_day_set = []

    waiting_hall_fills = []

    reviews_per_day = 0

    last_time_writing_reviews = 0

figures_counter = 0
cashbox_queue_lengths = [0,0]
serving_times = []
cashbox_queue_length_sets =[[],[]]
cashbox_queue_waiting_times =[[],[]]

lost = 0
lost_reviews = 0

last_seen_input_time = {}
queue_lengths = {}
waiting_times = {}
queue_length = {}
presence_times = {}
intensity_components = {}
service_intensity_components = {}

reviews_per_day_set = []

waiting_hall_fills = []


reviews_per_day = 0
day_length = 480

last_time_writing_reviews = 0

def get_last_seen_input_time(resource):
    try:
        return last_seen_input_time[resource]
    except:
        last_seen_input_time[resource] = -1
        return last_seen_input_time[resource]
    
def set_last_seen_input_time(resource, value):
    last_seen_input_time[resource] = value

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
    if (queue_length[resource] == 0):
        return
    append_value_to_collection(resource, queue_lengths, queue_length[resource])
    
def append_presence_time(resource, time):
    if (time == 0):
        return
    append_value_to_collection(resource, presence_times, time)
    
def get_presence_times(resource):
    return get_values_from_collection(resource, presence_times)

def append_intensity_component(resource, intensity_component):
    if (intensity_component == 0):
        return
    append_value_to_collection(resource, intensity_components, intensity_component)
    
def get_intensity_components(resource):
    return get_values_from_collection(resource, intensity_components)

def append_service_intensity_component(resource, intensity_component):
    if (intensity_component == 0):
        return
    append_value_to_collection(resource, service_intensity_components, intensity_component)
    
def get_service_intensity_components(resource):
    return get_values_from_collection(resource, service_intensity_components)
        
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
    global figures_counter
    plt.hist(collection,number_of_intervals)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()
    
def save_histogram(collection, number_of_intervals, title, xlabel, ylabel):
    global figures_counter
    plt.hist(collection,number_of_intervals)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig("figure_%i.png" % figures_counter)
    figures_counter += 1
    plt.gcf().clear()

class Statistics:
    def __init__(self, pdf) -> None:
        self.pdf = pdf

    def save_histogram_to_pdf(self, collection, number_of_intervals, title,
                               xlabel, ylabel) -> None:
        global figures_counter
        plt.hist(collection,number_of_intervals)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        figures_counter += 1

        self.pdf.savefig()
        plt.gcf().clear()

    
def increase_lost_quantity():
    global lost
    lost += 1
    
def increase_lost_reviews_quantity():
    global lost_reviews
    lost_reviews += 1


