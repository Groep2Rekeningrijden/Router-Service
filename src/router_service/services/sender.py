import json

# from masstransitpython import RabbitMQSender
from pydantic import BaseModel

from src.router_service.library_overrides.RabbitMQSender import RabbitMQSender


class Sender:
    def __init__(self, conf, exchange):
        self.exchange = exchange
        self.conf = conf

    def send_message(self, body, message: BaseModel):
        """
        :param message: Message object to send
        :param body: Message received from MassTransit client
        :return: None
        """
        with RabbitMQSender(self.conf) as sender:
            sender.set_exchange(exchange=self.exchange)

            encoded_msg = message.json(by_alias=True)
            response = sender.create_masstransit_response(encoded_msg, json.loads(body))
            sender.publish(message=response)
