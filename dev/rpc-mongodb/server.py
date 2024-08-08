import datetime
import json
import os
import sys
import traceback
import pika

from dev.utilities import create_connection, create_mongo_client

from pymongo import InsertOne

class RpcServer:
    def __init__(self):
        self.connection, self.channel = create_connection()
        self.mongo_client = create_mongo_client()

    def process_request(self):
        # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
        self.channel.queue_declare(queue='my-rpc-mongo-queue', durable=True)

        # Don't dispatch a new request to this server until it has processed and acknowledged the previous one
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(queue='my-rpc-mongo-queue', on_message_callback=self.on_request_received)

        print(' [*] Waiting for RPC requests. To exit press CTRL+C')
        self.channel.start_consuming()

    def on_request_received(self, ch, method, properties, body):
        # body is a byte sequence, e.g., b'573b0ae4-4ea8-11ef-a82a-0242ac130002'
        # so decode it to UTF-8
        taskId = body.decode('UTF-8')

        bson_data = {
            "task_id": taskId,
            "tags": ["mongodb", "python", "pymongo"],
            "date": datetime.datetime.now(tz=datetime.timezone.utc),
        }

        try:
            # Insert the bson data to MongoDB
            db = self.mongo_client.my_data # mongo_client["my_data"]
            collection = db.my_collection # db["my_collection"]
            
            # Insert single document
            # object_id = collection.insert_one(bson_data).inserted_id
            # document_id = str(object_id)

            # Bulk write
            requests = [InsertOne(bson_data)]
            bulk_write_result = collection.bulk_write(requests)
            print(f" [x] Inserted {bulk_write_result.inserted_count} document")

            response = {
                "db": "my_data",
                "collection": "my_collection",
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

# Usage: python -m dev.rpc-mongodb.server
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
