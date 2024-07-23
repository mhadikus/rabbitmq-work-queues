FROM python:3.9.13

RUN mkdir /mycode
WORKDIR /mycode

ADD . /mycode/

# Install Pika Python client for AMQP 0-9-1 protocol
RUN python -m pip install pika --upgrade

# Install retry decorator for retrying failed tasks
RUN python -m pip install retry --upgrade

ENTRYPOINT [ "/bin/sh" ]