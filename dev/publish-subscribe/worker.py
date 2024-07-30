import json
import os
import sys
import time
import pika

from dev.utilities import create_connection

# Usage: python -m dev.publish-subscribe.worker
def main():
    connection, channel = create_connection()

    # Set fanout exchange to broadcast messages to all queues
    channel.exchange_declare(exchange='my_fanout_exchange', exchange_type='fanout')

    # Create a queue whose name will be chosen by random by the server
    # Set exclusive=True to delete the queue once consumer connection is closed
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Binding to tell the exchange to send messages to our queue
    channel.queue_bind(exchange='my_fanout_exchange', queue=queue_name)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    # Don't dispatch a new message to this worker until it has processed and acknowledged the previous one
    # channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message_received, auto_ack=True)

    channel.start_consuming()

def on_message_received(ch, method, properties, body):
    # body is a byte sequence, e.g., b'{'Task': {'id': '0x1', 'duration': 2}}'
    decoded = body.decode('UTF-8')
    parsedJson = json.loads(decoded)
    print(f" [x] Received {parsedJson}")

    # Pretend to do the work by sleeping for the specified duration
    time.sleep(int(parsedJson['Task']['duration']))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)