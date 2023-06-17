"""
The receiver for masstransit.
"""
import gc
import logging
from json import loads, JSONDecodeError
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
        try:
            try:
                msg = loads(body.decode())
            except Exception as e:  # includes simplejson.decoder.JSONDecodeError
                print(f'Decoding JSON has failed with error: {str(e)}')
                raise e
            try:
                val = self.handler_func(msg["message"])
            except Exception as e:
                logging.error(f"Error in handler: {str(e)}")
                raise e
            if self.sender:
                try:
                    self.sender.send_message(body=body, message=val)
                except Exception as e:
                    logging.error(f"Error when sending: {str(e)}")
                    raise e
                del val
            else:
                return val
        except Exception:
            pass
        gc.collect()

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
