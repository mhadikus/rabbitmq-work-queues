import sys
import pika

from dev.hosts import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST
from dev.credentials import RABBITMQ_USER, RABBITMQ_PASSWORD

# Usage: python -m dev.publish-subscribe.producer [number_of_messages]
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
            virtual_host=RABBITMQ_VIRTUAL_HOST))

    channel = connection.channel()

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
