#!/usr/bin/env python3
"""
Helper script to set up VPC Flow Logs with proper IAM roles and CloudWatch log groups
"""

import boto3
import json
import time
from typing import Dict, Any

class FlowLogsSetup:
    def __init__(self, region_name: str = 'us-east-1'):
        self.region_name = region_name
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.iam_client = boto3.client('iam', region_name=region_name)
        self.logs_client = boto3.client('logs', region_name=region_name)
        self.sts_client = boto3.client('sts', region_name=region_name)
    
    def get_account_id(self) -> str:
        """Get current AWS account ID"""
        return self.sts_client.get_caller_identity()['Account']
    
    def create_flow_logs_role(self) -> str:
        """Create IAM role for VPC Flow Logs"""
        role_name = 'VPCFlowLogsRole'
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "vpc-flow-logs.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            print(f" IAM role {role_name} already exists")
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for VPC Flow Logs to write to CloudWatch'
            )
            print(f" Created IAM role {role_name}")
        
        # Create/update policy
        policy_name = 'VPCFlowLogsPolicy'
        try:
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            print(f" Attached policy {policy_name} to role")
        except Exception as e:
            print(f" Error creating policy: {e}")
        
        account_id = self.get_account_id()
        return f"arn:aws:iam::{account_id}:role/{role_name}"
    
    def create_log_group(self, log_group_name: str) -> bool:
        """Create CloudWatch log group"""
        try:
            self.logs_client.create_log_group(logGroupName=log_group_name)
            print(f" Created CloudWatch log group {log_group_name}")
            return True
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            print(f" CloudWatch log group {log_group_name} already exists")
            return True
        except Exception as e:
            print(f"  Error creating log group: {e}")
            return False
    
    def enable_vpc_flow_logs(self, vpc_id: str) -> Dict[str, Any]:
        """Enable VPC Flow Logs for the specified VPC"""
        log_group_name = f"VPCFlowLogs-{vpc_id}"
        
        print(f"🔧 Setting up VPC Flow Logs for {vpc_id}...")
        
        # Create IAM role
        role_arn = self.create_flow_logs_role()
        
        # Create log group
        if not self.create_log_group(log_group_name):
            return {'success': False, 'error': 'Failed to create log group'}
        
        # Wait a moment for IAM role to propagate
        print("⏳ Waiting for IAM role to propagate...")
        time.sleep(10)
        
        # Enable flow logs
        try:
            response = self.ec2_client.create_flow_logs(
                ResourceType='VPC',
                ResourceIds=[vpc_id],
                TrafficType='ALL',
                LogDestinationType='cloud-watch-logs',
                LogGroupName=log_group_name,
                DeliverLogsPermissionArn=role_arn,
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc-flow-log',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': f'FlowLogs-{vpc_id}'
                            },
                            {
                                'Key': 'CreatedBy',
                                'Value': 'VPCFlowLogAnalyzer'
                            }
                        ]
                    }
                ]
            )
            
            flow_log_ids = response.get('FlowLogIds', [])
            unsuccessful = response.get('Unsuccessful', [])
            
            if unsuccessful:
                error_msg = unsuccessful[0].get('Error', {}).get('Message', 'Unknown error')
                return {'success': False, 'error': error_msg}
            
            print(f"   Successfully enabled VPC Flow Logs")
            print(f"   Flow Log IDs: {flow_log_ids}")
            print(f"   Log Group: {log_group_name}")
            print(f"   IAM Role: {role_arn}")
            
            return {
                'success': True,
                'flow_log_ids': flow_log_ids,
                'log_group_name': log_group_name,
                'role_arn': role_arn
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    """Main function to set up VPC Flow Logs"""
    print("VPC Flow Logs Setup Helper")
    print("=" * 40)
    
    vpc_id = input("Enter VPC ID to enable Flow Logs: ").strip()
    
    if not vpc_id:
        print("VPC ID is required!")
        return
    
    region = input(f"Enter AWS region (default: us-east-1): ").strip() or 'us-east-1'
    
    try:
        setup = FlowLogsSetup(region_name=region)
        result = setup.enable_vpc_flow_logs(vpc_id)
        
        if result['success']:
            print(f"\n VPC Flow Logs successfully enabled!")
            print(f"\n Note: It may take 10-15 minutes for logs to start appearing.")
            print(f" You can now run the analyzer: python vpc_flow_analyzer.py")
        else:
            print(f"\n Failed to enable VPC Flow Logs: {result['error']}")
            
    except Exception as e:
        print(f"Setup failed: {e}")


if __name__ == "__main__":
    main()
