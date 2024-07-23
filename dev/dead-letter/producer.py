import sys
import traceback
import pika

from retry import retry
from dev.utilities import create_connection, initialize_queue_with_dead_letter

# Usage: python -m dev.dead-letter.producer [number_of_tasks] [number_of_errors]
#   Use the retry decorator. On connection failure, wait for a few seconds,
#   scaling up to a few minutes on consecutive failures.
@retry(delay=5, backoff=2, max_delay=180)
def start_producer():
    try:
        print(f"Start producing work...")
        connection, channel = create_connection()

        queue_name = 'my-work-2-queue'
        result = initialize_queue_with_dead_letter(channel, queue_name)
        print(f"Declared queue '{result.method.queue}'")

        # Throw if the server fails to confirm receipt of a message.
        channel.confirm_delivery()

        number_of_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        number_of_errors = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        produce_work(channel, queue_name, number_of_tasks, number_of_errors)

        # Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
        print(f"Closing connection")
        connection.close()
    except:
        print(f"Unexpected error: {traceback.format_exc()}")
        raise

def produce_work(channel, queue_name, number_of_tasks=1, number_of_errors=0):
    for i in range(number_of_tasks):
        # Send json data, e.g., {'Task': {'id': '0x1', 'duration': 2, 'error': false}}
        # If error is true, the worker will reject the message and it will be sent to the dead-letter exchange
        if i % 2 == 1 and number_of_errors > 0:
            error = True
            number_of_errors -= 1
        else:
            error = False
        duration = i + 1
        message = f"{{\"Task\": {{ \"id\": \"{hex(i)}\", \"duration\": {duration} }}, \"error\": {str(error).lower()} }}"

        # Use the default exchange (exchange_type='direct') identified by an empty string
        # Mark messages as persistent by supplying delivery_mode
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        print(f" [x] Sent '{message}'")

if __name__ == "__main__":
    start_producer()
