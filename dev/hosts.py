import os

def get_environment_variable(key: str, default="") -> str:
    return os.environ.get(key, default)

RABBITMQ_HOST = get_environment_variable("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = get_environment_variable("RABBITMQ_PORT", "5672")
RABBITMQ_VIRTUAL_HOST = get_environment_variable("RABBITMQ_VIRTUAL_HOST")

MINIO_URL = get_environment_variable("MINIO_URL", "http://minio:9000")

MONGODB_URI = get_environment_variable("MONGODB_URI")

ELASTICSEARCH_URL = get_environment_variable("ELASTICSEARCH_URL")
