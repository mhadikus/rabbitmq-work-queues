import pika, sys, os

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        credentials=pika.PlainCredentials('rabbitmq-dev', 'rabbitmq-dev'),
        virtual_host='my-virtual-host')
    )
    channel = connection.channel()

    channel.queue_declare(queue='my-simple-queue')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

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