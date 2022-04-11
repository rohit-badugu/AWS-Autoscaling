**Web tier's URL:** http://54.236.157.243:5001/process_image

**SQS queue names:**
- Request Queue: https://sqs.us-east-1.amazonaws.com/326395227693/RequestQueue
- Response Queue: https://sqs.us-east-1.amazonaws.com/326395227693/ResponseQueue

**Bucket names:**
- Input Bucket: input-bucket-96
- Output Bucket: output-bucket-96

**Command used to send requests:** python3 multithread_workload_generator_verify_results_updated.py  --num_request 100  --url 'http://54.236.157.243:5001/process_image'  --image_folder "face_images_100/"" 
