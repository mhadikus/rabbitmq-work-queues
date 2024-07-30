import pika
import boto3

from dev.hosts import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST, MINIO_URL
from dev.credentials import RABBITMQ_USER, RABBITMQ_PASSWORD, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD

def create_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
        virtual_host=RABBITMQ_VIRTUAL_HOST)
    )
    channel = connection.channel()
    return connection, channel

DEAD_LETTER_EXCHANGE_NAME = "dead-letter-exchange"

def initialize_queue_with_dead_letter(channel, queue_name):
    # Setup dead letter queue
    channel.exchange_declare(
        exchange=DEAD_LETTER_EXCHANGE_NAME,
        exchange_type="direct",
        durable=True
    )
    dead_letter_queue_name = queue_name + "-dead-letter"
    channel.queue_declare(queue=dead_letter_queue_name)
    dead_letter_exchange_key = queue_name + "-dead-letter-exchange-key"
    channel.queue_bind(
        exchange=DEAD_LETTER_EXCHANGE_NAME,
        routing_key=dead_letter_exchange_key,
        queue=dead_letter_queue_name,
    )

    # Setup and return the main queue
    return channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DEAD_LETTER_EXCHANGE_NAME,
            "x-dead-letter-routing-key": dead_letter_exchange_key,
            "x-queue-type": "quorum",
            "x-delivery-limit": 10})

def create_s3_client():
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_URL,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
    )
    return s3_client
