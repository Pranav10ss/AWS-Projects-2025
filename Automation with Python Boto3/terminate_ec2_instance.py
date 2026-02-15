import boto3
aws_management_console = boto3.session.Session(profile_name="Boto3-User")
ec2_console = aws_management_console.client('ec2')
response = ec2_console.terminate_instances(
    InstanceIds=[
        'i-02f135283f48aa861'
    ]
)