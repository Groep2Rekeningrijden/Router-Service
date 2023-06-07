"""
Router service.
"""
import os

from masstransitpython import RabbitMQConfiguration
from pika import PlainCredentials
from src.router_service.services.receiver import Receiver
from src.router_service.services.route_handler import RouteHandler
from src.router_service.services.sender import Sender

RABBITMQ_USERNAME = os.environ["RABBITMQ_USERNAME"]
RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]
RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT = int(os.environ["RABBITMQ_PORT"])
RABBITMQ_VIRTUAL_HOST = os.environ["RABBITMQ_VIRTUAL_HOST"]
RABBITMQ_QUEUE = os.environ["RABBITMQ_QUEUE"]
MASSTRANSIT_INPUT = os.environ["MASSTRANSIT_INPUT"]
MASSTRANSIT_OUTPUT = os.environ["MASSTRANSIT_OUTPUT"]


def run():
    """
    Run the router service.
    """
    credentials = PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

    conf = RabbitMQConfiguration(
        credentials,
        queue=RABBITMQ_QUEUE,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VIRTUAL_HOST,
    )
    route_handler = RouteHandler()
    sender = Sender(conf, MASSTRANSIT_OUTPUT)
    receiver = Receiver(conf, MASSTRANSIT_INPUT, route_handler.handle, sender)
    receiver.start()


if __name__ == "__main__":
    """
    Run the service.
    """
    run()
