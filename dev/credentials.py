import os
from typing import Union

def _get_credential(key: str,default="") -> Union[str, None]:
    return os.environ.get(key, default)

RABBITMQ_USER = _get_credential("RABBITMQ_USER")
RABBITMQ_PASSWORD = _get_credential("RABBITMQ_PASSWORD")
RABBITMQ_VIRTUAL_HOST = _get_credential("RABBITMQ_VIRTUAL_HOST")
