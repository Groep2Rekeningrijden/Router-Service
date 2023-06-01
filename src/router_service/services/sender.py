from json import loads

from masstransitpython import RabbitMQSender

from src.router_service.services.message_encoder import MessageEncoder


class Sender:
    def __init__(self, conf, exchange):
        self.exchange = exchange
        self.conf = conf

    def send_message(self, body, message: object):
        '''
        :param message: Message object to send
        :param body: Message received from MassTransit client
        :return: None
        '''
        with RabbitMQSender(self.conf) as sender:
            sender.set_exchange(exchange=self.exchange)

            encoded_msg = MessageEncoder().encode(message)
            response = sender.create_masstransit_response(loads(encoded_msg), body)
            sender.publish(message=response)
