import os
from typing import Union

def get_environment_variable(key: str, default="") -> str:
    return os.environ.get(key, default)

RABBITMQ_USER = get_environment_variable("RABBITMQ_USER")
RABBITMQ_PASSWORD = get_environment_variable("RABBITMQ_PASSWORD")
