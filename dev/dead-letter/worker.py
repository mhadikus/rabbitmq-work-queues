import json
import os
import sys
import time
import traceback
import pika

from retry import retry
from dev.utilities import create_connection

# Usage: python -m dev.dead-letter.worker
#   Use the retry decorator. On connection failure, wait for a few seconds,
#   scaling up to a few minutes on consecutive failures.
@retry(delay=5, backoff=2, max_delay=180)
def consume_work():
    try:
        print(f"Start consuming work...")
        connection, channel = create_connection()

        # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
        channel.queue_declare(queue='my-work-queue', durable=True)

        # Don't dispatch a new message to this worker until it has processed and acknowledged the previous one
        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(queue='my-work-queue', on_message_callback=on_message_received)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except:
        print(f"Unexpected error: {traceback.format_exc()}")
        raise

def on_message_received(ch, method, properties, body):
    # body is a byte sequence, e.g., b'{'Task': {'id': '0x1', 'duration': 2}}'
    decoded = body.decode('UTF-8')
    parsedJson = json.loads(decoded)
    print(f" [x] Received {parsedJson}")

    # Pretend to do the work by sleeping for the specified duration
    time.sleep(int(parsedJson['Task']['duration']))

    # If an error occurred, reject the message and it will be sent to the dead-letter exchange
    if parsedJson['error']:
        # ch.basic_reject(delivery_tag = method.delivery_tag, requeue=False)
        print(f" [x] Rejected Task id: {parsedJson['Task']['id']}")

    # Manually ack the message
    # A timeout (30 minutes by default) is enforced on consumer delivery acknowledgement
    ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    try:
        consume_work()
    except KeyboardInterrupt:
        print('\nStopping consumer\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)