import pika, sys, os

from dev.utilities import create_connection

# Usage: python -m dev.simple-queue.receive
def main():
    connection, channel = create_connection()

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