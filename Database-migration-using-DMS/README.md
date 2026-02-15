In this project, we will be migrating a simple web application from the on-premise environment to AWS. 
The on-premises environment is a virtual web server simulated using EC2 and a self managed MariaDB database server, which is also simulated via EC2. 

We will be migrating this into AWS & running the architecture on an EC2 web server together with an RDS managed SQL database.
We will be performing this migration using AWS DMS (Database migration service). 

## STAGE 1 - Implement the base infrastructure
In this stage we will simulate the on-premise environment (shown in the left side of the architecture diagram) and the base AWS infrastructure (shown on the right).


* [Calling AMI public parameters in Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-public-parameters-ami.html)