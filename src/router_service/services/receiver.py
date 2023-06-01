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
        receiver = RabbitMQReceiver(self.conf, self.exchange)
        receiver.add_on_message_callback(self.handler)
        receiver.start_consuming()
