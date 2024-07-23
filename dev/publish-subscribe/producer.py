import sys
import pika

from dev.utilities import create_connection

# Usage: python -m dev.publish-subscribe.producer [number_of_messages]
def main():
    connection, channel = create_connection()

    # Set fanout exchange to broadcast messages to all queues
    channel.exchange_declare(exchange='my_fanout_exchange', exchange_type='fanout')

    number_of_messages = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    for i in range(number_of_messages):
        # Send json data, e.g., {'Task': {'id': '0x1', 'duration': 2}}
        duration = i + 1
        message = f"{{\"Task\": {{ \"id\": \"{hex(i)}\", \"duration\": {duration} }} }}"

        # Publish to the named exchange
        channel.basic_publish(
            exchange='my_fanout_exchange',
            routing_key='',
            body=message)
        print(f" [x] Sent '{message}'")

    # Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
    connection.close()

if __name__ == "__main__":
    main()
