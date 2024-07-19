# RabbitMQ Work Queues with Docker and Python
 Using RabbitMQ to distribute tasks among workers using the competing consumers pattern

## Starting RabbitMQ and Management Plugin with Docker Compose

Build an image for running producer and consumers with Python<br/>
`docker build -t producer-consumer .`

Create and start containers in the background (-d detached mode)<br/>
`docker-compose --env-file docker-compose-dev.env up -d`

[/dev/simple-queue](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/simple-queue): send and receive a single message<br/>
- `python send.py` sends a single message
- `python receive.py` waits and consumes the message

# References

 - [RabbitMQ Setup with Docker](https://medium.com/@buttraheel6/simplifying-rabbitmq-setup-with-docker-a-step-by-step-guide-9698dc9ea4ff)
 - [RabbitMQ Work Queues Tutorials](https://www.rabbitmq.com/tutorials#2-work-queues)