"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from time import sleep
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.p_id = ''

    def run(self):
        self.p_id = self.marketplace.register_producer()
        while True:
            for prod_info in self.products:
                for _ in range(prod_info[1]):
                    sleep(prod_info[2])
                    while not self.marketplace.publish(self.p_id, prod_info[0]):
                        sleep(self.republish_wait_time)
