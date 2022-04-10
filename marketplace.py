"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from uuid import uuid4
import unittest


import logging
from logging.handlers import RotatingFileHandler

from threading import Lock
import time

from .product import Product


def logger_set_up():
    """
    Configures logging for marketplace class.
    """
    logging.basicConfig(
        handlers=[RotatingFileHandler(
            'marketplace.log', maxBytes=10000, backupCount=10)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')

    logging.Formatter.converter = time.gmtime


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer: int):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        logger_set_up()
        self.queue_size_per_producer = queue_size_per_producer

        self.producers_queues: dict[str, list[Product]] = {}
        self.available_products: dict[Product, int] = {}
        self.carts: dict[int, list] = {}
        self.customer_lock = Lock()
        self.producer_lock = Lock()
        self.printing_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logging.info('register producer started.')
        with self.producer_lock:
            p_id = uuid4().hex
            self.producers_queues[p_id] = []
        logging.info('register producer finished. Returned %s.', p_id)
        return p_id

    def publish(self, producer_id: str, product: Product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        logging.info(
            'publish started. Parameters: producer_id = %s, product = %s.', producer_id, product)
        # check if the given producer has available space in queue

        if len(self.producers_queues[producer_id]) == self.queue_size_per_producer:
            logging.info('publish finished. Returned False.')
            return False

        # add product in the producer's list
        self.producers_queues[producer_id].append(product)

        # increase product availability
        if product not in self.available_products:
            self.available_products[product] = 1
        else:
            self.available_products[product] += 1

        logging.info('publish finished. Returned True.')
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        logging.info('new_cart started.')
        with self.customer_lock:
            cart_id = uuid4().int
            self.carts[cart_id] = []
        logging.info('new_cart finished. Returned %i', cart_id)
        return cart_id

    def add_to_cart(self, cart_id: int, product: Product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logging.info(
            'add_to_cart started. Parameters: cart_id=%i, product=%s.', cart_id, product)

        with self.customer_lock:

            # check if product is available
            if product not in self.available_products or self.available_products[product] == 0:
                logging.info('add_to_cart finished. Returned False.')
                return False

            # decrement availability
            self.available_products[product] -= 1

            # add product in cart
            self.carts[cart_id].append(product)

        logging.info('add_to_cart finished. Returned True.')
        logging.debug('added')
        return True

    def remove_from_cart(self, cart_id: int, product: Product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logging.info(
            'remove_from_cart started. Parameters: cart_id=%i, product=%s.', cart_id, product)
        with self.customer_lock:
            # remove product form cart
            self.carts[cart_id].remove(product)

            # increment availability
            self.available_products[product] += 1
        logging.info('remove_from_cart finished.')

    def place_order(self, cart_id: int):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logging.info('place_order started. Parameters: cart_id=%i.', cart_id)
        # remove cart products from stock
        bought_items = []

        for product in self.carts[cart_id]:
            for producer_queue in self.producers_queues.values():
                if product in producer_queue:
                    bought_items.append(product)
                    producer_queue.remove(product)
                    break

        logging.info('place_order finished. Returned %s.', bought_items)
        return bought_items


class TestMarketplace(unittest.TestCase):
    """
    Testing class for Marketplace class.
    """

    def setUp(self):
        """
        Sets up an object for testing
        """
        self.marketplace = Marketplace(1)

    def test_register_producer_return_str(self):
        """
        Tests register_producer functionality
        """
        p_id = self.marketplace.register_producer()
        self.assertEqual(type(p_id), str)

    def test_new_cart_return_int(self):
        """
        Tests new_cart functionality
        """
        c_id = self.marketplace.new_cart()
        self.assertEqual(type(c_id), int)

    def test_publish_if_queue_not_full_then_return_true(self):
        """
        Tests publish functionality in case of full queue
        """
        p_id = self.marketplace.register_producer()
        self.assertEqual(self.marketplace.publish(p_id, Product('Tea', 11)),
                         True)

    def test_publish_if_queue_full_then_return_true(self):
        """
        Tests publish functionality
        """
        p_id = self.marketplace.register_producer()
        self.marketplace.publish(p_id, Product('Tea', 11))
        self.assertEqual(self.marketplace.publish(
            p_id, Product('Tea', 11)), False)

    def test_add_to_cart_if_product_not_available_return_false(self):
        """
        Tests add_to_cart when the product is not available
        """
        c_id = self.marketplace.new_cart()
        self.assertEqual(self.marketplace.add_to_cart(
            c_id, Product('Tea', 11)), False)

    def test_add_to_cart_if_product_available_return_true(self):
        """
        Tests add_to_cart when the product is available
        """
        c_id = self.marketplace.new_cart()
        p_id = self.marketplace.register_producer()
        self.marketplace.publish(p_id, Product('Tea', 11))

        self.assertEqual(self.marketplace.add_to_cart(
            c_id, Product('Tea', 11)), True)

    def test_remove_from_cart(self):
        """
        Tests remove_from_cart
        """
        c_id = self.marketplace.new_cart()
        p_id = self.marketplace.register_producer()
        self.marketplace.publish(p_id, Product('Tea', 11))
        self.marketplace.add_to_cart(
            c_id, Product('Tea', 11))
        self.marketplace.remove_from_cart(c_id, Product('Tea', 11))
        self.assertEqual(len(self.marketplace.carts[c_id]), 0)

    def test_place_order(self):
        """
        Tests place_order
        """
        p_id = self.marketplace.register_producer()
        c_id = self.marketplace.new_cart()
        self.marketplace.publish(p_id, Product('Tea', 11))
        self.marketplace.add_to_cart(
            c_id, Product('Tea', 11))
        self.marketplace.place_order(c_id)
        self.assertEqual(len(self.marketplace.producers_queues[p_id]), 0)
