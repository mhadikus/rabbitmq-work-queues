import datetime
import json
import os
import sys
import traceback
import pika

from dev.utilities import create_connection, create_elasticsearch_client
from elasticsearch.helpers import bulk

class RpcServer:
    def __init__(self):
        self.connection, self.channel = create_connection()
        self.elasticsearch_client = create_elasticsearch_client()
        self.elasticsearch_index = "my_index"

    def process_request(self):
        # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
        self.channel.queue_declare(queue='my-rpc-elasticsearch-queue', durable=True)

        # Don't dispatch a new request to this server until it has processed and acknowledged the previous one
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(queue='my-rpc-elasticsearch-queue', on_message_callback=self.on_request_received)

        print(' [*] Waiting for RPC requests. To exit press CTRL+C')
        self.channel.start_consuming()

    def on_request_received(self, ch, method, properties, body):
        # body is a byte sequence, e.g., b'573b0ae4-4ea8-11ef-a82a-0242ac130002'
        # so decode it to UTF-8
        taskId = body.decode('UTF-8')
        try:
            bulk_actions = self.create_actions_to_insert(taskId)

            # https://elasticsearch-py.readthedocs.io/en/latest/helpers.html
            bulk(self.elasticsearch_client, bulk_actions)

            response = {
                "index": self.elasticsearch_index,
                "task_id": taskId,
            }
            response_as_string = json.dumps(response)

            # Publish the response to the named exchange
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id = properties.correlation_id),
                body=response_as_string)
            print(f" [x] Sent: {response_as_string}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            print(f"Unexpected error: {traceback.format_exc()}")
            raise

    def create_actions_to_insert(self, taskId):
        date = datetime.datetime.now(tz=datetime.timezone.utc)
        date_string = date.strftime("%B %d, %Y") # e.g., 'September 13, 2024'

        data_to_insert = {
            "task_id": taskId,
            "tags": ["elasticsearch", "python"],
            "date": date,
            "description": f"Request #{taskId} received from client on {date_string}"
        }

        actions = {
            "_index": self.elasticsearch_index,
             "_id": taskId,
            "_source": data_to_insert
        }

        return [ actions ]

# Usage: python -m dev.rpc-elasticsearch.server
def main():
    rpc_server = RpcServer()
    rpc_server.process_request()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
