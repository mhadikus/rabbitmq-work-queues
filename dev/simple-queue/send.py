import pika

from dev.utilities import create_connection

# Usage: python -m dev.simple-queue.send
def main():
    connection, channel = create_connection()

    channel.queue_declare(queue='my-simple-queue')

    # Use the default exchange (exchange_type='direct') identified by an empty string
    channel.basic_publish(exchange='', routing_key='my-simple-queue', body='Simple Task')
    print(" [x] Sent 'Simple Task'")

    # Ensure network buffers were flushed and our message was actually delivered to RabbitMQ
    connection.close()

if __name__ == "__main__":
    main()
