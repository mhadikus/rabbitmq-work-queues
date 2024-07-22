import pika, sys, os

from dev.hosts import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST
from dev.credentials import RABBITMQ_USER, RABBITMQ_PASSWORD

# Usage: python -m dev.simple-queue.receive
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
        virtual_host=RABBITMQ_VIRTUAL_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue='my-simple-queue')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    # Turn off manual ack by setting auto_ack=True
    channel.basic_consume(queue='my-simple-queue', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)