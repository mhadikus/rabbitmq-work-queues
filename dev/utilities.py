import traceback
import pika
import boto3
import pymongo

from pymongo.server_api import ServerApi

from dev.hosts import \
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST, \
    MINIO_URL, \
    MONGODB_URI
from dev.credentials import \
    RABBITMQ_USER, RABBITMQ_PASSWORD, \
    MINIO_ROOT_USER, MINIO_ROOT_PASSWORD, \
    MONGODB_USER, MONGODB_PW

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

def create_mongo_client():
    mongo_host = MONGODB_URI.format(username=MONGODB_USER, password=MONGODB_PW)
    client = pymongo.MongoClient(
        mongo_host,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=30000)
    # MongoClient ctor does not block
    # and does not raise ConnectionFailure/ConfigurationError if credentials are wrong.
    # Check the connection with ping.
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient
    try:
        client.admin.command("ping")
    except Exception:
        # Rethrow if there is a connection error.
        message = "Error connecting to Mongo Server\n" f"{traceback.format_exc()}"
        print(message)
        raise
    return client
