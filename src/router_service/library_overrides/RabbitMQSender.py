"""
The custom RabbitMQ Sender class.
"""
import logging
import uuid

from pika import BlockingConnection, ConnectionParameters
from src.router_service.models.message_envelope import MessageEnvelope


class RabbitMQSender(object):
    """
    The custom RabbitMQ Sender class.
    """

    __slots__ = [
        "_configuration",
        "_connection",
        "_channel",
        "_queue",
        "_routing_key",
        "_exchange",
    ]

    def __init__(self, configuration):
        """
        Create the RabbitMQ Sender.

        :param configuration: RabbitMQConfiguration object
        """
        self._configuration = configuration
        self._connection = BlockingConnection(
            ConnectionParameters(
                host=self._configuration.host,
                port=self._configuration.port,
                virtual_host=self._configuration.virtual_host,
                credentials=self._configuration.credentials,
            )
        )
        self._channel = self._connection.channel()
        self._queue = self._configuration.queue
        self._channel.queue_declare(queue=self._queue)
        self._routing_key = ""
        self._exchange = ""

    def __enter__(self):
        """
        Return self for use in 'using'.

        :return: self
        """
        return self

    def set_routing_key(self, routing_key=""):
        """
        Set the routing key.

        :param routing_key: the routing key
        """
        self._routing_key = routing_key

    def set_exchange(self, exchange=""):
        """
        Set the exchange.

        :param exchange: The exchange.
        """
        self._exchange = exchange
        self._channel.exchange_declare(
            exchange=self._exchange, exchange_type="fanout", durable=True
        )

    def publish(self, message):
        """
        Publish the message.

        :param message: JSON string
        """
        # self._channel.
        self._channel.basic_publish(
            exchange=self._exchange, routing_key=self._routing_key, body=message
        )
        logging.warning(f"Message published to {self._queue} queue\n")

    def create_masstransit_response(self, message, request_body):
        """
        Create a masstransit compatible response envelope.

        :param message: The message to be sent.
        :param request_body: The body of a previous masstransit message.
        :return: The MessageEnvelope containing the necessary entries
        """
        return MessageEnvelope(
            messageId=uuid.uuid4(),
            conversationId=request_body["conversationId"],
            messageType=["urn:message:" + self._exchange],
            message=message,
        ).json(by_alias=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the connection and exit, for use in 'using'.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self._connection.close()
