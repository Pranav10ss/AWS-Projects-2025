# import all the modules and libraries
import boto3
from pprint import pprint

# open management console session using profile name
aws_management_console = boto3.session.Session(profile_name="default")

# Open IAM console
iam_console = aws_management_console.client(service_name='iam')

result = iam_console.list_users()

for each_user in result['Users']:
    pprint(each_user['UserName'])