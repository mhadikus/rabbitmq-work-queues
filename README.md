# RabbitMQ Work Queues with Docker and Python
 Using RabbitMQ to distribute tasks among workers using producer consumer patterns

## Starting RabbitMQ and Management Plugin with Docker Compose

Build an image for running producer and consumers with Python<br/>
- `docker build -t producer-consumer .`

Create and start containers in the background (-d detached mode)<br/>
- `docker-compose --env-file docker-compose-dev.env up -d`
- http://localhost:15673 to view the management dashboard

[/dev/simple-queue](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/simple-queue): send and receive a single message<br/>
- `python -m dev.simple-queue.send` sends a single message
- `python -m dev.simple-queue.receive` waits and consumes the message

[/dev/work-queue](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/work-queue): distributing tasks among workers (competing consumers pattern)<br/>
- `python -m dev.work-queue.producer [number_of_tasks]` queue a number of tasks
- `python -m dev.work-queue.worker` consumes and acks the message

[/dev/publish-subscribe](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/publish-subscribe): deliver messages to multiple consumers (publish/subscribe)<br/>
- `python -m dev.publish-subscribe.producer [number_of_messages]` broadcasts messages to all queues
- `python -m dev.publish-subscribe.worker` subscribes to consume the published messages

# References

 - [RabbitMQ Setup with Docker](https://medium.com/@buttraheel6/simplifying-rabbitmq-setup-with-docker-a-step-by-step-guide-9698dc9ea4ff)
 - [RabbitMQ Work Queues Tutorials](https://www.rabbitmq.com/tutorials#2-work-queues)
