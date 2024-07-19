import pika

from hosts import RABBITMQ_HOST, RABBITMQ_PORT
from credentials import RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_VIRTUAL_HOST

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
        virtual_host=RABBITMQ_VIRTUAL_HOST))


channel = connection.channel()

channel.queue_declare(queue='my-simple-queue')

# Use the default exchange identified by an empty string
channel.basic_publish(exchange='', routing_key='my-simple-queue', body='Simple Task')
print(" [x] Sent 'Simple Task'")

# Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
connection.close()