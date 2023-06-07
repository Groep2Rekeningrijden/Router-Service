"""
The receiver for masstransit.
"""
import logging
from json import loads
from time import sleep

import pika.exceptions
from masstransitpython import RabbitMQReceiver
from src.router_service.services.sender import Sender


class Receiver:
    """
    The receiver for masstransit.
    """

    def __init__(self, conf, exchange, handler_func, sender: Sender = None):
        self.sender = sender
        self.handler_func = handler_func
        self.conf = conf
        self.exchange = exchange

    def handler(
        self,
        ch,
        method,
        properties,
        body,
    ):
        """
        Trigger this when a message is consumed from the queue.

        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        msg = loads(body.decode())
        val = self.handler_func(msg["message"])
        if self.sender:
            self.sender.send_message(body=body, message=val)
        else:
            return val

    def start(self):
        """
        Start consuming on the receiver.

        :return:
        """
        # define receiver
        receiver = None
        attempts = 0
        while attempts < 10:
            try:
                receiver = RabbitMQReceiver(self.conf, self.exchange)
                break
            # TODO: Pretty sure this isn't the right error to catch...
            except pika.exceptions.ConnectionWrongStateError as e:
                logging.warning(f"Connection to rabbitmq failed {attempts} times...")
                attempts += 1
                sleep(5)
                if attempts >= 10:
                    raise e

        receiver.add_on_message_callback(self.handler)
        receiver.start_consuming()
