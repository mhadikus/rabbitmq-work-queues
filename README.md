# RabbitMQ Python Work Queues with Docker (and AWS S3/MinIO)
 Using RabbitMQ to distribute tasks among workers using various producer consumer patterns

## Starting RabbitMQ and Management Plugin with Docker Compose

Build an image for running producer and consumers with Python<br/>
- `docker build -t producer-consumer .`

Create and start containers in the background (-d detached mode)<br/>
- `docker-compose --env-file docker-compose-dev.env up -d`
- http://localhost:15673 to view the management dashboard

[/dev/simple-queue](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/simple-queue): send and receive a single message<br/>
- `python -m dev.simple-queue.send` send a single message
- `python -m dev.simple-queue.receive` wait and consume the message

[/dev/work-queue](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/work-queue): distributing tasks among workers (competing consumers pattern)<br/>
- `python -m dev.work-queue.producer [number_of_tasks]` queue a number of tasks
- `python -m dev.work-queue.worker` consume and ack the message

[/dev/publish-subscribe](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/publish-subscribe): deliver messages to multiple consumers (publish/subscribe)<br/>
- `python -m dev.publish-subscribe.producer [number_of_messages]` broadcast messages to all queues
- `python -m dev.publish-subscribe.worker` subscribe to consume the published messages

[/dev/dead-letter](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/dead-letter): configure a dead letter exchange<br/>
- `python -m dev.publish-subscribe.producer [number_of_tasks] [number_of_errors]`
  - queue a number of tasks marked with zero or more errors
- `python -m dev.publish-subscribe.worker`
  - consume and ack the task, or send it to the dead letter queue if `error` is `true`

[/dev/rpc-minio](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/rpc-minio): request/reply [RPC](https://www.rabbitmq.com/tutorials#6-rpc) pattern with [MinIO](https://min.io/) and AWS [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#using-boto3) client<br/>
- `python -m dev.rpc-minio.server`
  - wait for RPC requests from clients, create json data as the response, and store it in MinIO bucket
- `python -m dev.rpc-minio.client`
  - send an RPC request to the server, read the response json data from the MinIO bucket and print it
- http://localhost:9001 to view the MinIO object store

## How to debug with Visual Studio Code

- Install the following extensions
  - [Docker](https://code.visualstudio.com/docs/containers/overview) extension to debug containerized applications
  - [Dev Containers](https://code.visualstudio.com/docs/devcontainers/tutorial#_install-the-extension) to run Visual Studio Code inside a Docker container
  - Restart Visual Studio Code
- In the Docker tab, right click on the container and select _Attach Visual Studio Code_
  - This opens a new window that is attached to the container
  - Install the Python extension on the container
  - Restart Visual Studio Code
- Start debugging with [launch.json](https://github.com/mhadikus/rabbitmq-work-queues/tree/main/dev/launch.json) configuration file

# References

 - [RabbitMQ Setup with Docker](https://medium.com/@buttraheel6/simplifying-rabbitmq-setup-with-docker-a-step-by-step-guide-9698dc9ea4ff)
 - [RabbitMQ Queue Tutorials](https://www.rabbitmq.com/tutorials#queue-tutorials)
 - [Developing inside a Container with VS Code](https://code.visualstudio.com/docs/devcontainers/containers)
 - [Pika Python Documentation](https://pika.readthedocs.io/en/stable)
 - [Celery Python Documentation](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)
   - [What does Celery offer that Pika doesn't?](https://stackoverflow.com/questions/23766658/rabbitmq-what-does-celery-offer-that-pika-doesnt)
