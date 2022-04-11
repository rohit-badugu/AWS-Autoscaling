from flask import Flask, request
from server.utils import send_image_to_queue
import base64
import os
import uuid
import time

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    request_id = str(uuid.uuid4())
    os.makedirs('active_requests', exist_ok=True)

    request_file_name = 'active_requests/' + request_id + '.txt'
    with open(request_file_name, 'w') as f:
        f.write("")
        
    uploaded_file = request.files['myfile']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        with open(uploaded_file.filename, "rb") as image:
            b64string = base64.b64encode(image.read())
            b64string = b64string.decode('utf-8')
            
            send_image_to_queue(request_id, uploaded_file.filename, b64string)
        os.remove(uploaded_file.filename)

        result_file_name = 'results/' + request_id + '.txt'
        while not os.path.exists(result_file_name):
            time.sleep(1)

        os.remove(request_file_name)
        result = ""
        with open(result_file_name, 'r') as file:
            result = file.read().rstrip()
        os.remove(result_file_name)
        return result
    else:
        return "Error processing request: " + request_id
    

@app.route("/")
def index():
    return "<p>Nothing</p>"
