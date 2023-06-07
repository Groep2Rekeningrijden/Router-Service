"""
Sender for masstransit.
"""
import json

from pydantic import BaseModel
from src.router_service.library_overrides.RabbitMQSender import RabbitMQSender


class Sender:
    """
    Sender for masstransit.
    """

    def __init__(self, conf, exchange):
        self.exchange = exchange
        self.conf = conf

    def send_message(self, body, message: BaseModel):
        """
        Send a message to the exchange.

        :param message: Message object to send
        :param body: Message received from MassTransit client
        :return: None
        """
        with RabbitMQSender(self.conf) as sender:
            sender.set_exchange(exchange=self.exchange)

            response = sender.create_masstransit_response(message, json.loads(body))
            sender.publish(message=response)
