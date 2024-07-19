import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq-server',
        port=5672,
        credentials=pika.PlainCredentials('rabbitmq-dev', 'rabbitmq-dev'),
        virtual_host='my-virtual-host'))


channel = connection.channel()

channel.queue_declare(queue='my-simple-queue')

# Use the default exchange identified by an empty string
channel.basic_publish(exchange='', routing_key='my-simple-queue', body='Simple Task')
print(" [x] Sent 'Simple Task'")

# Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
connection.close()