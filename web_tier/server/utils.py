import boto3

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/RequestQueue'
RESPONSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/326395227693/ResponseQueue'

sqs = boto3.client('sqs')


def send_image_to_queue(request_id, image_name, image_data):

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=REQUEST_QUEUE_URL,
        MessageAttributes={
            'RequestID': {
                'DataType': 'String',
                'StringValue': request_id
            },
            'ImageName': {
                'DataType': 'String',
                'StringValue': image_name
            },
        },
        MessageBody=(
            image_data
        )
    )

    print("Request sent: " + request_id)

    print(response['MessageId'])
