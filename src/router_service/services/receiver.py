import logging
from time import sleep

from masstransitpython import RabbitMQReceiver
from json import loads

from src.router_service.services.sender import Sender


class Receiver:
    def __init__(self, conf, exchange, handler_func, sender: Sender = None):
        self.sender = sender
        self.handler_func = handler_func
        self.conf = conf
        self.exchange = exchange

    def handler(self, ch, method, properties, body, ):
        msg = loads(body.decode())
        print(f"Received request for: {msg['message']['VehicleId']}")
        val = self.handler_func(msg["message"])
        if self.sender:
            self.sender.send_message(body=body, message=val)
        else:
            return val

    def start(self):
        # define receiver
        receiver = None
        attempts = 0
        while attempts < 10:
            try:
                receiver = RabbitMQReceiver(self.conf, self.exchange)
                break
            except Exception as e:
                logging.warning(f"Connection to rabbitmq failed {attempts} times...")
                attempts += 1
                sleep(5)
                if attempts >= 10:
                    raise e

        receiver.add_on_message_callback(self.handler)
        receiver.start_consuming()
