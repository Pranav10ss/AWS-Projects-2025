#!/usr/bin/env python3
"""
AWS Bedrock VPC Flow Log Analyzer
Analyzes VPC Flow Logs using AWS Bedrock for natural language queries
"""

import boto3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This class will get all the details from .env file and store it here 
class VPCFlowLogAnalyzer:
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the VPC Flow Log Analyzer with AWS clients"""
        self.region_name = region_name
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.logs_client = boto3.client('logs', region_name=region_name)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        
    def check_vpc_exists(self, vpc_id: str) -> bool:
        """Check if the VPC exists"""
        try:
            response = self.ec2_client.describe_vpcs(VpcIds=[vpc_id])
            return len(response['Vpcs']) > 0
        except Exception as e:
            logger.error(f"Error checking VPC existence: {e}")
            return False
    
    def check_flow_logs_enabled(self, vpc_id: str) -> Dict[str, Any]:
        """Check if VPC Flow Logs are enabled for the given VPC"""
        try:
            response = self.ec2_client.describe_flow_logs(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [vpc_id]
                    }
                ]
            )
            
            flow_logs = response.get('FlowLogs', [])
            active_flow_logs = [fl for fl in flow_logs if fl['FlowLogStatus'] == 'ACTIVE']
            
            return {
                'enabled': len(active_flow_logs) > 0,
                'flow_logs': active_flow_logs,
                'total_count': len(flow_logs),
                'active_count': len(active_flow_logs)
            }
        except Exception as e:
            logger.error(f"Error checking flow logs: {e}")
            return {'enabled': False, 'error': str(e)}
    
    def get_flow_log_data(self, vpc_id: str, hours_back: int = 24) -> List[Dict]:
        """Retrieve VPC Flow Log data from CloudWatch Logs"""
        flow_logs_info = self.check_flow_logs_enabled(vpc_id)
        
        if not flow_logs_info['enabled']:
            return []
        
        # Get the log group name from flow logs
        log_groups = []
        for flow_log in flow_logs_info['flow_logs']:
            if flow_log.get('LogDestinationType') == 'cloud-watch-logs':
                log_group_name = flow_log.get('LogGroupName')
                if log_group_name:
                    log_groups.append(log_group_name)
        
        if not log_groups:
            logger.warning("No CloudWatch log groups found for VPC Flow Logs")
            return []
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        all_logs = []
        
        for log_group in log_groups:
            try:
                response = self.logs_client.filter_log_events(
                    logGroupName=log_group,
                    startTime=int(start_time.timestamp() * 1000),
                    endTime=int(end_time.timestamp() * 1000),
                    limit=1000  # Limit to prevent overwhelming responses
                )
                
                for event in response.get('events', []):
                    log_entry = self.parse_flow_log_entry(event['message'])
                    if log_entry:
                        all_logs.append(log_entry)
                        
            except Exception as e:
                logger.error(f"Error retrieving logs from {log_group}: {e}")
        
        return all_logs
    
    def parse_flow_log_entry(self, log_message: str) -> Optional[Dict]:
        """Parse a VPC Flow Log entry"""
        try:
            # VPC Flow Log format: version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes windowstart windowend action flowlogstatus
            fields = log_message.strip().split()
            
            if len(fields) >= 14:
                return {
                    'version': fields[0],
                    'account_id': fields[1],
                    'interface_id': fields[2],
                    'srcaddr': fields[3],
                    'dstaddr': fields[4],
                    'srcport': fields[5],
                    'dstport': fields[6],
                    'protocol': fields[7],
                    'packets': fields[8],
                    'bytes': fields[9],
                    'windowstart': fields[10],
                    'windowend': fields[11],
                    'action': fields[12],
                    'flowlogstatus': fields[13]
                }
        except Exception as e:
            logger.error(f"Error parsing log entry: {e}")
        
        return None
    
    def format_flow_logs_for_bedrock(self, flow_logs: List[Dict], max_records: int = 100) -> str:
        """Format flow logs in a compact way for Bedrock analysis"""
        if not flow_logs:
            return "No flow log data available."
        
        # Limit records to avoid token limits
        limited_logs = flow_logs[:max_records]
        
        # Create a more compact format
        formatted_data = "VPC Flow Log Records:\n"
        formatted_data += "Format: SrcIP -> DstIP:Port (Protocol) [Action] Bytes/Packets\n\n"
        
        for i, log in enumerate(limited_logs, 1):
            protocol_name = self.get_protocol_name(log.get('protocol', ''))
            formatted_data += f"{i:3d}. {log.get('srcaddr', 'N/A')}:{log.get('srcport', 'N/A')} -> "
            formatted_data += f"{log.get('dstaddr', 'N/A')}:{log.get('dstport', 'N/A')} "
            formatted_data += f"({protocol_name}) [{log.get('action', 'N/A')}] "
            formatted_data += f"{log.get('bytes', 'N/A')}B/{log.get('packets', 'N/A')}P\n"
        
        if len(flow_logs) > max_records:
            formatted_data += f"\n... and {len(flow_logs) - max_records} more records\n"
        
        return formatted_data
    
    def get_protocol_name(self, protocol_num: str) -> str:
        """Convert protocol number to name"""
        protocol_map = {
            '1': 'ICMP',
            '6': 'TCP', 
            '17': 'UDP',
            '47': 'GRE',
            '50': 'ESP',
            '51': 'AH'
        }
        return protocol_map.get(protocol_num, f'Protocol-{protocol_num}')
    
    def analyze_flow_logs_summary(self, flow_logs: List[Dict]) -> Dict[str, Any]:
        """Generate a summary analysis of flow logs"""
        if not flow_logs:
            return {'message': 'No flow log data available'}
        
        df = pd.DataFrame(flow_logs)

        # Input for the model
        summary = {
            'total_records': len(df),
            'unique_source_ips': df['srcaddr'].nunique(),
            'unique_destination_ips': df['dstaddr'].nunique(),
            'top_source_ips': df['srcaddr'].value_counts().head(10).to_dict(),
            'top_destination_ips': df['dstaddr'].value_counts().head(10).to_dict(),
            'top_ports': df['dstport'].value_counts().head(10).to_dict(),
            'actions': df['action'].value_counts().to_dict(),
            'protocols': df['protocol'].value_counts().to_dict(),
            'total_bytes': df['bytes'].astype(int).sum(),
            'total_packets': df['packets'].astype(int).sum()
        }
        
        return summary

    # query the Amazon Bedrock with natural language questions about the flow logs
    def query_bedrock(self, prompt: str, flow_log_data: List[Dict], hours_back: int = 24) -> str:
        """Query AWS Bedrock with natural language questions about flow logs"""
        try:
            # Format flow log data for Bedrock
            flow_log_text = self.format_flow_logs_for_bedrock(flow_log_data, max_records=150)
            
            # Get summary for additional context
            summary = self.analyze_flow_logs_summary(flow_log_data)
            
            # Create a comprehensive prompt for Bedrock with actual data
            system_prompt = f"""
            You are an AWS VPC Flow Log analyst with access to detailed VPC Flow Log data from the last {hours_back} hours.
            
            SUMMARY STATISTICS:
            - Time Range: Last {hours_back} hours
            - Total Records: {summary.get('total_records', 0)}
            - Unique Source IPs: {summary.get('unique_source_ips', 0)}
            - Unique Destination IPs: {summary.get('unique_destination_ips', 0)}
            - Total Bytes: {summary.get('total_bytes', 0):,}
            - Total Packets: {summary.get('total_packets', 0):,}
            
            ACTUAL FLOW LOG DATA:
            {flow_log_text}

            # Letting know the model what it can/should do
            IMPORTANT INSTRUCTIONS:
            - You have access to the actual detailed flow log records above
            - When asked for specific information (IPs, ports, protocols), extract and list the actual values from the data
            - For questions like "what source IPs do you see", list the actual IP addresses from the records
            - For questions about ports, protocols, actions - provide the specific values you see
            - Be precise and use the actual data, not just summaries
            - If asked for top/most frequent items, analyze the actual records and count occurrences
            - Always reference specific record numbers when providing examples
            """
            
            # Prepare the request for Claude 3 Sonnet
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,  # Increased for more detailed responses
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error querying Bedrock: {e}")
            return f"Error analyzing data: {str(e)}"
    
    def enable_flow_logs_instructions(self, vpc_id: str) -> str:
        """Provide instructions to enable VPC Flow Logs"""
        return f"""
        VPC Flow Logs are not enabled for VPC {vpc_id}. 
        
        To enable VPC Flow Logs, you can:
        
        1. Using AWS CLI:
        aws ec2 create-flow-logs \\
            --resource-type VPC \\
            --resource-ids {vpc_id} \\
            --traffic-type ALL \\
            --log-destination-type cloud-watch-logs \\
            --log-group-name VPCFlowLogs \\
            --deliver-logs-permission-arn arn:aws:iam::YOUR-ACCOUNT-ID:role/flowlogsRole
        
        2. Using AWS Console:
        - Go to VPC Dashboard
        - Select your VPC ({vpc_id})
        - Go to Flow Logs tab
        - Click "Create flow log"
        - Choose destination (CloudWatch Logs recommended)
        - Set up IAM role for delivery
        
        3. Required IAM Role Policy:
        {{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": {{
                        "Service": "vpc-flow-logs.amazonaws.com"
                    }},
                    "Action": "sts:AssumeRole"
                }}
            ]
        }}
        
        After enabling, wait 10-15 minutes for logs to start appearing.
        """


def main():
    """Main function to run the VPC Flow Log Analyzer"""
    print("🔍 AWS Bedrock VPC Flow Log Analyzer")
    print("=" * 50)
    
    # Get VPC ID from user
    vpc_id = input("Enter VPC ID: ").strip()
    
    if not vpc_id:
        print(" VPC ID is required!")
        return
    
    # Initialize analyzer
    try:
        analyzer = VPCFlowLogAnalyzer()
        print(f" Initialized analyzer for region: {analyzer.region_name}")
    except Exception as e:
        print(f" Failed to initialize AWS clients: {e}")
        return
    
    # Check if VPC exists
    print(f"\n Checking if VPC {vpc_id} exists...")
    if not analyzer.check_vpc_exists(vpc_id):
        print(f" VPC {vpc_id} not found in region {analyzer.region_name}")
        return
    
    print(f" VPC {vpc_id} found")
    
    # Check if Flow Logs are enabled
    print(f"\n Checking VPC Flow Logs status...")
    flow_logs_info = analyzer.check_flow_logs_enabled(vpc_id)
    
    if flow_logs_info.get('error'):
        print(f" Error checking flow logs: {flow_logs_info['error']}")
        return
    
    if not flow_logs_info['enabled']:
        print(f" VPC Flow Logs are not enabled for VPC {vpc_id}")
        print("\n Instructions to enable VPC Flow Logs:")
        print(analyzer.enable_flow_logs_instructions(vpc_id))
        return
    
    print(f" VPC Flow Logs are enabled ({flow_logs_info['active_count']} active)")
    
    # Get time range from user
    print(f"\n How many hours of flow log data would you like to analyze?")
    print("   Examples: 1 (last hour), 6 (last 6 hours), 24 (last day), 168 (last week)")
    
    while True:
        try:
            hours_input = input("Enter hours (default: 24): ").strip()
            if not hours_input:
                hours_back = 24
                break
            hours_back = int(hours_input)
            if hours_back <= 0:
                print(" Please enter a positive number of hours")
                continue
            if hours_back > 8760:  # More than a year
                print("  Warning: Requesting more than a year of data may be slow")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    break
                else:
                    continue
            break
        except ValueError:
            print(" Please enter a valid number")
    
    # Get flow log data
    print(f"\n Retrieving flow log data (last {hours_back} hours)...")
    flow_logs = analyzer.get_flow_log_data(vpc_id, hours_back)
    
    if not flow_logs:
        print("  No flow log data found. This could mean:")
        print("   - Flow logs were recently enabled (wait 10-15 minutes)")
        print(f"   - No traffic in the last {hours_back} hours")
        print("   - Flow logs are configured to send to S3 instead of CloudWatch")
        return
    
    print(f" Retrieved {len(flow_logs)} flow log entries")
    
    # Show summary
    summary = analyzer.analyze_flow_logs_summary(flow_logs)
    print(f"\n Flow Log Summary:")
    print(f"   Total Records: {summary['total_records']}")
    print(f"   Unique Source IPs: {summary['unique_source_ips']}")
    print(f"   Unique Destination IPs: {summary['unique_destination_ips']}")
    print(f"   Total Bytes: {summary['total_bytes']:,}")
    print(f"   Total Packets: {summary['total_packets']:,}")
    
    # Interactive query loop
    print(f"\n You can now ask natural language questions about your VPC Flow Logs!")
    print("Examples:")
    print("- 'What are the top source IP addresses?'")
    print("- 'Show me rejected connections'")
    print("- 'What protocols are being used most?'")
    print("- 'Are there any suspicious activities?'")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            question = input(" Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print(" Goodbye!")
                break
            
            if not question:
                continue
            
            print(" Analyzing...")
            answer = analyzer.query_bedrock(question, flow_logs, hours_back)
            print(f"\n Answer: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
