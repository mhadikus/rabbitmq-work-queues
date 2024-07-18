FROM python:3.9.13

RUN mkdir /mycode
WORKDIR /mycode

ADD ./dev /mycode/

# Install Pika Python client for AMQP 0-9-1 protocol
RUN python -m pip install pika --upgrade

ENTRYPOINT [ "/bin/sh" ]