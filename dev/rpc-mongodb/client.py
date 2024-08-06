import json
import os
import pprint
import sys
import traceback
import pika
import uuid

from dev.utilities import create_connection, create_mongo_client

from bson.objectid import ObjectId

class RpcClient:
    def __init__(self):
        self.connection, self.channel = create_connection()

        self.mongo_client = create_mongo_client()

        # Declare an exclusive callback queue for replies
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        print(f" [x] Declared exclusive callback queue {self.callback_queue}")

        # Subscribe to the callback queue to receive RPC responses
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        # Check if the correlation_id is the one we're looking for
        # If so, save the response and break the consuming loop
        if self.corr_id == props.correlation_id:
            try:
                # The response body contains the document ID in MongoDB
                response_as_string = body.decode('UTF-8')
                response = json.loads(response_as_string)
                db =  self.mongo_client[response["db"]]
                collection = db[response["collection"]]
                response_data = collection.find_one({"_id": ObjectId(response["_id"])})
                self.response = response_data
            except:
                print(f"Unexpected error: {traceback.format_exc()}")
                raise

    def send_request(self, taskId):
        self.response = None

        # Generate a unique correlation_id for the request
        self.corr_id = str(uuid.uuid4())

        # Publish the request with two properties: reply_to and correlation_id
        self.channel.basic_publish(
            exchange='',
            routing_key='my-rpc-queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(taskId))

        # Wait until the proper response arrives and return the response
        while self.response is None:
            self.connection.process_data_events(time_limit=None)

        return self.response

# Usage: python -m dev.rpc-mongodb.client
def main():
    rpc_client = RpcClient()

    # Set task ID to a UUID based on the host ID and current time
    taskId = uuid.uuid1()

    print(f" [x] Requesting {taskId}")
    response = rpc_client.send_request(taskId)
    print(" [.] Received :")
    pprint.pprint(response)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted\n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)