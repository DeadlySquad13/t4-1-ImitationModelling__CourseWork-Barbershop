from dataclasses import dataclass

import numpy

import constants
import statistics
from statistics import Statistics
from matplotlib.backends import backend_pdf
from entities import Entities
from simulation import Simulation

waiting_hall_fill = 0

blocked = False

#rqs = [0,0]

@dataclass
class BarberShopStatistics():
    _simulation = Simulation()

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
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(self._simulation.entities.cashbox_one), 50,
                                  "Waiting time in cashbox one queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(self._simulation.entities.cashbox_two), 10,
                                  "Waiting time in cashbox two queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(self._simulation.entities.short_hairing_hall), 50,
                                  "Waiting time in short hairing hall queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(self._simulation.entities.fashion_hairing_hall), 50,
                                  "Waiting time in fashion hairing hall queue", "length of waiting (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_waiting_times(self._simulation.entities.colouring_hall), 50,
                                  "Waiting time in colouring hall queue", "length of waiting (minutes)", "quantity of clients")

            _statistics.save_histogram_to_pdf(statistics.get_presence_times(self._simulation.entities.cashbox_one), 50,
                                  "Presence time in cashbox one", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(self._simulation.entities.cashbox_two), 10,
                                  "Presence time in cashbox two", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(self._simulation.entities.short_hairing_hall), 50,
                                  "Presence time in short hairing hall", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(self._simulation.entities.fashion_hairing_hall), 50,
                                  "Presence time in fashion hairing hall", "length of presence (minutes)", "quantity of clients")
            _statistics.save_histogram_to_pdf(statistics.get_presence_times(self._simulation.entities.colouring_hall), 50,
                                  "Presence time in colouring hall queue", "length of presence (minutes)", "quantity of clients")

    def log(self):
        """TODO: What it does, what's the purpose?
        """
        print("Average cashbox one queue length = \t%f" % numpy.mean(statistics.get_queue_lengths(self._simulation.entities.cashbox_one)))
        print("Average cashbox two queue length = \t%f" % numpy.mean(statistics.get_queue_lengths(self._simulation.entities.cashbox_two)))
        print("Average short hairing queue length = \t%f" % numpy.mean(statistics.get_queue_lengths(self._simulation.entities.short_hairing_hall)))
        print("Average fashion hairing queue length = \t%f" % numpy.mean(statistics.get_queue_lengths(self._simulation.entities.fashion_hairing_hall)))
        print("Average colouring queue length = \t%f" % numpy.mean(statistics.get_queue_lengths(self._simulation.entities.colouring_hall)))
        
        print("Cashbox one input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.cashbox_one)))
        print("Cashbox two input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.cashbox_two)))
        print("Short hairing hall input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.short_hairing_hall)))
        print("Fashion hairing hall input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.fashion_hairing_hall)))
        print("Colouring hall input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.colouring_hall)))
        print("Review desk input intensity = \t%f" % numpy.mean(statistics.get_intensity_components(self._simulation.entities.review_desk)))
        
        print("Average cashbox one waiting time = \t%f" % numpy.mean(statistics.get_waiting_times(self._simulation.entities.cashbox_one)))
        print("Average cashbox two waiting time = \t%f" % numpy.mean(statistics.get_waiting_times(self._simulation.entities.cashbox_two)))
        print("Average short hairing waiting time = \t%f" % numpy.mean(statistics.get_waiting_times(self._simulation.entities.short_hairing_hall)))
        print("Average fashion hairing waiting time =\t %f" % numpy.mean(statistics.get_waiting_times(self._simulation.entities.fashion_hairing_hall)))
        print("Average colouring waiting time = \t%f" % numpy.mean(statistics.get_waiting_times(self._simulation.entities.colouring_hall)))
        
        print("Average cashbox one presence time = \t%f" % numpy.mean(statistics.get_presence_times(self._simulation.entities.cashbox_one)))
        print("Average cashbox two presence time = \t%f" % numpy.mean(statistics.get_presence_times(self._simulation.entities.cashbox_two)))
        print("Average short hairing presence time = \t%f" % numpy.mean(statistics.get_presence_times(self._simulation.entities.short_hairing_hall)))
        print("Average fashion hairing presence time = \t%f" % numpy.mean(statistics.get_presence_times(self._simulation.entities.fashion_hairing_hall)))
        print("Average colouring presence time = \t%f" % numpy.mean(statistics.get_presence_times(self._simulation.entities.colouring_hall)))
        
        print("Average cashbox one service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.cashbox_one)))
        print("Average cashbox two service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.cashbox_two)))
        print("Average short hairing service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.short_hairing_hall)))
        print("Average fashion hairing service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.fashion_hairing_hall)))
        print("Average colouring service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.colouring_hall)))
        print("Average review desk service intensity = \t%f" % numpy.mean(statistics.get_service_intensity_components(self._simulation.entities.review_desk)))
        
        print("Losing review probability = \t%f" % (statistics.lost_reviews/constants.number_of_clients))
        print("Losing client probability = \t%f" % (statistics.lost/constants.number_of_clients))


if (constants.statistics_enable):
    barber_shop_statistics = BarberShopStatistics()
    barber_shop_statistics.save_to_pdf('barber_shop_statistics.pdf')

