from pickle import OBJ
import boto3
from PIL import Image
import io
import base64
import os
from face_recognition import face_match

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/RequestQueue'
RESPONSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/ResponseQueue'

INPUT_BUCKET = 'input-bucket-96'
OUTPUT_BUCKET = 'output-bucket-96'

def poll_and_process_image_from_queue():
    sqs = boto3.client('sqs')

    while True:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=REQUEST_QUEUE_URL,
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
            print("Request received: " + request_id)

            image_name = message['MessageAttributes']['ImageName']['StringValue']
            image_data = message['Body']

            os.makedirs('received', exist_ok=True)

            file_name = 'received/' + image_name

            with open(file_name, "wb") as fh:
                temp = bytes(image_data, encoding="utf-8")
                fh.write(base64.decodebytes(temp))

            result = ""
            result = face_match(file_name, 'data.pt')
            result = result[0]
            send_image_recognition_result(request_id, result)
            push_image_and_result_to_s3(image_name, file_name, result)

            os.remove(file_name)
            
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=REQUEST_QUEUE_URL,
                ReceiptHandle=receipt_handle
            )

def push_image_and_result_to_s3(image_name, image_full_path, image_result):
    s3 = boto3.resource('s3')
    s3.Bucket(INPUT_BUCKET).upload_file(image_full_path, image_name)
    s3.Object(OUTPUT_BUCKET, os.path.splitext(image_name)[0]).put(Body=image_result)

def send_image_recognition_result(request_id, image_result):
    sqs = boto3.client('sqs')

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=RESPONSE_QUEUE_URL,
        MessageAttributes={
            'RequestID': {
                'DataType': 'String',
                'StringValue': request_id
            },
            'ImageResult': {
                'DataType': 'String',
                'StringValue': image_result
            },
        },
        MessageBody=(
            image_result
        )
    )

    print("Result for request sent: " + request_id)

    print(response['MessageId'])

if __name__ == "__main__":
    print("Starting image poller")
    poll_and_process_image_from_queue()
