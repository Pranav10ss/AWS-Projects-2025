import boto3
from pprint import pprint
aws_management_console = boto3.session.Session(profile_name="Boto3-User")
ec2_console = aws_management_console.client(service_name='ec2')
result = ec2_console.describe_instances()['Reservations']

for each_instance in result:
    for value in each_instance['Instances']:
        print(value['InstanceId'])