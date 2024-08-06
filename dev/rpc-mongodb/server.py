import datetime
import json
import os
import sys
import traceback
import pika

from dev.utilities import create_connection, create_mongo_client

# Usage: python -m dev.rpc-mongodb.server
def main():
    connection, channel = create_connection()

    # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
    channel.queue_declare(queue='my-rpc-queue', durable=True)

    # Don't dispatch a new request to this server until it has processed and acknowledged the previous one
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='my-rpc-queue', on_message_callback=on_request_received)

    print(' [*] Waiting for RPC requests. To exit press CTRL+C')
    channel.start_consuming()

def on_request_received(ch, method, properties, body):
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
        mongo_client = create_mongo_client()
        db = mongo_client.my_data # mongo_client["my_data"]
        collection = db.my_collection # db["my_collection"]
        object_id = collection.insert_one(bson_data).inserted_id
        document_id = str(object_id)

        response = {
            "db": "my_data",
            "collection": "my_collection",
            "_id": document_id,
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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
