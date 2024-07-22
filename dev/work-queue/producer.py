import sys
import pika

from dev.hosts import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST
from dev.credentials import RABBITMQ_USER, RABBITMQ_PASSWORD

# Usage: python -m dev.work-queue.producer [number_of_tasks]
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
            virtual_host=RABBITMQ_VIRTUAL_HOST))

    channel = connection.channel()

    # Ensure the queue can survive a RabbitMQ node restart by setting durable=True
    channel.queue_declare(queue='my-work-queue', durable=True)

    number_of_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    for i in range(number_of_tasks):
        # Every dot accounts for one second of work
        # Send json data, e.g., {'Task': {'id': '0x1', 'duration': 2}}
        duration = i + 1
        message = f"{{\"Task\": {{ \"id\": \"{hex(i)}\", \"duration\": {duration} }} }}"

        # Use the default exchange identified by an empty string
        # Mark messages as persistent by supplying delivery_mode
        channel.basic_publish(
            exchange='',
            routing_key='my-work-queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        print(f" [x] Sent '{message}'")

    # Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
    connection.close()

if __name__ == "__main__":
    main()
