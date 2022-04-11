import boto3
import os

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/RequestQueue'
RESPONSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/ResponseQueue'

def poll_and_process_results_from_queue():
    sqs = boto3.client('sqs')

    while True:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=RESPONSE_QUEUE_URL,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            WaitTimeSeconds=20
        )
        
        if 'Messages' in response and len(response['Messages']) > 0:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            request_id = message['MessageAttributes']['RequestID']['StringValue']
            print("Processing result for request: " + request_id)

            image_result = message['MessageAttributes']['ImageResult']['StringValue']

            os.makedirs('results', exist_ok=True)

            file_name = 'results/' + request_id + '.txt'
            with open(file_name, 'w') as f:
                f.write(image_result)
            
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=RESPONSE_QUEUE_URL,
                ReceiptHandle=receipt_handle
            )

if __name__ == "__main__":
    print("Starting results poller")
    poll_and_process_results_from_queue()