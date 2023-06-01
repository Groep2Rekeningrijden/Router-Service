import sys
import traceback

import pika
import json
import re
import logging
import logging.handlers


def create_mass_transit_response(result, request_body, namespace):
    # It creates a message according to the Masstransit requirements. More info
    # http://masstransit-project.com/MassTransit/advanced/interoperability.html
    response = {
        'requestId': request_body['requestId'],
        'correlationId': request_body['correlationId'],
        'conversationId': request_body['conversationId'],
        'initiatorId': request_body['correlationId'],
        'sourceAddress': request_body['destinationAddress'],
        'destinationAddress': request_body['sourceAddress'],
        'messageType': [
            f'urn:message:{namespace}'  # namespace = INTERFACE_NAMESPACE_HERE:YOUR_CSHARP_INTERFACE_NAME
        ],

        # The `message` value/object must implement the interface mentioned on messageType
        'message': result
    }

    return json.dumps(response)


def get_exchange_name(address):
    # It just extract the exchange name from a URI
    parts = re.search('/(\w+)\?', address)
    return parts.group(1)


class MasstransitConsumer:

    def __init__(self, publisher_exchange_name, consumer_queue_name, callback):
        self.PUBLISHER_EXCHANGE_NAME = publisher_exchange_name
        self.CONSUMER_QUEUE_NAME = consumer_queue_name
        self.callback_func = callback
        # Logging config
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ])
        logger = logging.getLogger()

    def callback(self, ch, method, props, body):
        logging.info(f"Message received - CorrelationId={props.correlation_id}")
        logging.debug("Message contents:\n'{0}'".format(body))
        try:
            # Message format is:
            #   public string VehicleId { get; set; } = string.Empty;
            #   public List<Coordinates> Cords { get; set; } = new List<Coordinates>();
            #         public double Lat { get; set; }
            #         public double Long { get; set; }
            #         public DateTime TimeStamp { get; set; }
            request = json.loads(body.decode('UTF-8'))
            self.callback_func(request.message.Coordinates)

        # try:
        #     request = json.loads(body.decode('UTF-8'))
        #
        #     # Do some stuff
        #
        #     result = 'some string result... It could be an object'
        #
        #     exchange = get_exchange_name(request['responseAddress'])
        #     logging.debug("Exchange extracted from responseAddress request: '{0}'".format(exchange))
        #
        #     response_body = create_mass_transit_response(result, request, self.PUBLISHER_EXCHANGE_NAME)
        #     logging.debug("Response body for MassTransit:\n'{0}'".format(response_body))
        #
        #     # Respond to the initiator exchange extracted from request['responseAddress']
        #     ch.basic_publish(exchange,
        #                      routing_key=exchange,
        #                      properties=pika.BasicProperties(correlation_id=props.correlation_id),
        #                      body=response_body)

        except Exception as e:
            logging.error("error {0}".format(e))
            logging.error(traceback.format_exc())

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info("Message handling complete")

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Make sure that we have an Exchange created the same way as masstransit creates one
        channel.exchange_declare(exchange=self.PUBLISHER_EXCHANGE_NAME, exchange_type='fanout', durable=True)

        channel.queue_declare(queue=self.CONSUMER_QUEUE_NAME,
                              exclusive=False,
                              auto_delete=True,
                              durable=False)

        channel.queue_bind(queue=self.CONSUMER_QUEUE_NAME, exchange=self.PUBLISHER_EXCHANGE_NAME)
        channel.basic_consume(queue=self.CONSUMER_QUEUE_NAME, on_message_callback=self.callback)

        channel.start_consuming()
