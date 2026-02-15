# Essential files used in the project
## Main Application
`vpc_flow_analyzer` is the main analyzer application built using Python
Running this application provides an interactive CLI with Bedrock AI integration. 
Run the following command to use this application.

```
python vpc_flow_analyzer.py
```

## VPC Flow Logs Setup helper
`setup_flow_logs.py` is used to automatically enable VPC Flow Logs if it isn't already enabled.
It creates IAM Roles, CloudWatch log groups and enables Flow Logs for the VPC. 
Run the following command.

```
python setup_flow_logs.py
```
## Configuration files
* `requirements.txt` is used to install python dependencies
* `.env.example` is a template consisting of environment variables
* `config.py` is file consisting of configuration management

## Utility files
* `activate_env.sh` is the virtual environment activation script.
  - Usage: `./activate_env.sh`

