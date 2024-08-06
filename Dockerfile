FROM python:3.9.13

RUN mkdir /mycode
WORKDIR /mycode

ADD . /mycode/

# Install Pika Python client for AMQP 0-9-1 protocol
RUN python -m pip install pika --upgrade

# Install retry decorator for retrying failed tasks
RUN python -m pip install retry --upgrade

# Install boto3 for AWS S3/MinIO operations
RUN python -m pip install boto3 --upgrade

# Install PyMongo (Python driver for MongoDB)
RUN python -m pip install pymongo --upgrade

ENTRYPOINT [ "/bin/sh" ]