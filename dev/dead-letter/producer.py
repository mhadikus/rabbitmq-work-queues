import sys
import pika

from dev.utilities import create_connection

# Usage: python -m dev.dead-letter.producer [number_of_tasks]
def produce_work():
    print(f"Start producing work...")
    connection, channel = create_connection()

    # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
    channel.queue_declare(queue='my-work-queue', durable=True)

    number_of_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    for i in range(number_of_tasks):
        # Send json data, e.g., {'Task': {'id': '0x1', 'duration': 2}}
        duration = i + 1
        message = f"{{\"Task\": {{ \"id\": \"{hex(i)}\", \"duration\": {duration} }} }}"

        # Use the default exchange (exchange_type='direct') identified by an empty string
        # Mark messages as persistent by supplying delivery_mode
        channel.basic_publish(
            exchange='',
            routing_key='my-work-queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        print(f" [x] Sent '{message}'")

    # Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
    print(f"Closing connection\n")
    connection.close()

if __name__ == "__main__":
    produce_work()
