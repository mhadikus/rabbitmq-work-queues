import json
import os
import sys
import time
import pika

from dev.hosts import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST
from dev.credentials import RABBITMQ_USER, RABBITMQ_PASSWORD

# Usage: python -m dev.work-queue.worker
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
        virtual_host=RABBITMQ_VIRTUAL_HOST)
    )
    channel = connection.channel()

    # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
    channel.queue_declare(queue='my-work-queue', durable=True)

    # Don't dispatch a new message to this worker until it has processed and acknowledged the previous one
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='my-work-queue', on_message_callback=on_message_received)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def on_message_received(ch, method, properties, body):
    # body is a byte sequence, e.g., b'{'Task': {'id': '0x1', 'duration': 2}}'
    decoded = body.decode('UTF-8')
    parsedJson = json.loads(decoded)
    print(f" [x] Received {parsedJson}")

    # Pretend to do the work by sleeping for the specified duration
    time.sleep(int(parsedJson['Task']['duration']))

    # Manually ack the message
    ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)