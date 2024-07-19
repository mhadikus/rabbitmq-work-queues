import os

def get_environment_variable(key_name: str, default: str) -> str:
    return os.environ.get(key_name, default)

RABBITMQ_HOST = get_environment_variable("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = get_environment_variable("RABBITMQ_PORT", "5672")
