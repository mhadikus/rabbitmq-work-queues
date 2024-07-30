import os
import sys
import traceback
import pika
import boto3

from dev.utilities import create_connection, create_s3_client

# Usage: python -m dev.rpc-minio.server
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

    response = f"{{\"Task\": {{ \"id\": \"{taskId}\"}} }}"

    try:
        # Put the response to S3 bucket
        s3_client = create_s3_client()
        s3_client.put_object(Body=response, Bucket="my-bucket-1", Key=taskId, ContentType="application/json")

        # Publish the object key (taskId) to the named exchange
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id = properties.correlation_id),
            body=taskId)
        print(f" [x] Sent {taskId}")

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
