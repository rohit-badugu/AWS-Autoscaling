import os
import boto3
import time
import math

AMI_ID = 'ami-073a61bd9ab8a27fd'

MIN_INSTANCES = 0
MAX_INSTANCES = 20

def get_all_instance_names():
    instance_names = []
    for i in range(MIN_INSTANCES+1, MAX_INSTANCES+1):
        instance_names.append("app-instance" + str(i))
    return instance_names

def create_instance():
    ec2_client = boto3.client("ec2")
    instances = ec2_client.run_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="cc-proj",
        SecurityGroupIds=['sg-0bff9a326ac665f62'],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': get_available_instance_name()
                    },
                ],
            }            
        ]
    )

    print("Started instance: " + instances["Instances"][0]["InstanceId"])

def get_available_instance_name():
    running_instances, running_instances_ids = get_running_instances()
    running_instances = set(running_instances)
    all_names = set(get_all_instance_names())
    available_names = all_names.difference(running_instances)
    return list(available_names)[0]

def get_running_instances():
    ec2_client = boto3.client("ec2")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["pending","running"],
        },
        {
            "Name": "tag:Name",
            "Values": get_all_instance_names()
        }
    ]).get("Reservations")

    running_instances = []
    running_instances_ids = []
    for reservation in reservations:
        for instance in reservation["Instances"]:
            running_instances.append(instance["Tags"][0]["Value"])
            running_instances_ids.append(instance["InstanceId"])

    # print(running_instances)
    return (running_instances, running_instances_ids)

def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print("Terminated instance: " + instance_id)

def autoscale():    
    os.makedirs('active_requests', exist_ok=True)
    while True:
        DIR = 'active_requests'
        pending_requests = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

        instances_should_be_running = math.ceil(pending_requests/4)
        instances_should_be_running = max(MIN_INSTANCES, instances_should_be_running)
        instances_should_be_running = min(MAX_INSTANCES, instances_should_be_running)

        (running_instances, running_instances_ids) = get_running_instances()

        currently_running_instances = len(running_instances_ids)

        if currently_running_instances > instances_should_be_running:
            instances_to_shutdown = currently_running_instances - instances_should_be_running 
            print("Scaling down: " + str(instances_to_shutdown) + " instances")
            for i in range(0, instances_to_shutdown):
                terminate_instance(running_instances_ids[i])
        elif instances_should_be_running > currently_running_instances:
            instances_to_start = instances_should_be_running - currently_running_instances
            print("Scaling up: " + str(instances_to_start) + " instances")
            for i in range(0, instances_to_start):
                create_instance()
        else:
            print("No change")
        time.sleep(15)

if __name__ == "__main__":
    print("Starting controller")
    autoscale()
