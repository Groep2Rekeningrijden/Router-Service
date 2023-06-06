"""
Router service.
"""

from masstransitpython import RabbitMQConfiguration
from pika import PlainCredentials

from src.router_service.services.receiver import Receiver
from src.router_service.services.route_handler import RouteHandler
from src.router_service.services.sender import Sender

RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
# RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_VIRTUAL_HOST = '/'


def run():
    """
    Run the router service.
    """
    credentials = PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

    conf = RabbitMQConfiguration(credentials,
                                 queue='RouterPy',
                                 host=RABBITMQ_HOST,
                                 port=RABBITMQ_PORT,
                                 virtual_host=RABBITMQ_VIRTUAL_HOST)
    route_handler = RouteHandler("Brussels, Belgium")
    sender = Sender(conf, 'Data_Service.DTOs:RouteDTO')
    receiver = Receiver(conf, 'Coordinate_Service.DTOs:PublishCoordinatesDTO', route_handler.handle, sender)
    receiver.start()


if __name__ == "__main__":
    """
    Run the service.
    """
    run()
