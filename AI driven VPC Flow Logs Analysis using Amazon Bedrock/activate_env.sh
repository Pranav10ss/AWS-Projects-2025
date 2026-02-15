#!/bin/bash
# Activation script for VPC Flow Log Analyzer environment

echo "   Activating VPC Flow Log Analyzer environment..."
source vpc-analyzer-env/bin/activate

echo "   Virtual environment activated!"
echo "   Available commands:"
echo "   python vpc_flow_analyzer.py     - Run the main analyzer"
echo "   python setup_flow_logs.py      - Set up VPC Flow Logs"
echo "   python demo_analyzer.py        - Run demo with sample data"
echo "   python test_aws_connection.py  - Test AWS connectivity"
echo ""
echo "  Type 'deactivate' to exit the virtual environment"

# Keep the shell active
exec $SHELL
