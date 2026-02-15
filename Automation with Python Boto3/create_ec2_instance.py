import boto3

aws_management_console = boto3.session.Session(
    profile_name="Boto3-User"
    )
ec2_console = aws_management_console.client('ec2')
response = ec2_console.run_instances(
    ImageId='ami-068c0051b15cdb816',
    InstanceType='t2.micro',
    MaxCount=1,
    MinCount=1
)