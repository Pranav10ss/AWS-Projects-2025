# Host the app on EC2 to add traffic to thr VPC Flow Logs
## 1. Create an EC2 instance
Create an EC2 instance. 
Use the **default VPC**.
Create a **security group** with the following **inbound rules**:
```
Inbound rules
IP version   Type    Protocol    Port range        Source
IPv4         HTTP    TCP         80                0.0.0.0/0
Ipv4         SSH     TCP         22                0.0.0.0/0
```
Make sure the EC2 instance is in a **public subnet**. 
The **Route table** attached to the subnet should allow traffic from the destination `0.0.0.0/0` with target as the VPC's `igw-123456`.
Also make sure that the **NACL** attached to the VPC is allowing the inbound traffic from the following ports:
```
Inbound rules
Rule#    Type                Protocol    Port Range       Source        Allow/Deny
100      SSH(22)             TCP (6)     22              0.0.0.0/0        ALLOW
101      HTTP(80)            TCP (6)     80              0.0.0.0/0        ALLOW
```

## 2. Run the App on the EC2 instance
* Connect to the instance using **EC2 instance connect**.
Make sure you have downloaded the key pair to authenticate to the instance.
cd into the folder where the key pair file is located.
* Run the Following commands and host the application.
```sh
# Upload files to EC2 using SCP
scp -i demo-ai-vpc-flow-logs.pem index.html photo.jpg ec2-user@ec2-3-90-219-31.compute-1.amazonaws.com:/tmp

# Connect to EC2 instance
ssh -i demo-ai-vpc-flow-logs.pem ec2-user@ec2-3-90-219-31.compute-1.amazonaws.com

# Verify uploaded files
ls /tmp

# Install nginx
sudo dnf install -y nginx

# Start nginx service
sudo systemctl start nginx

# Enable nginx on boot
sudo systemctl enable nginx

# Move website files to nginx web root
sudo mv /tmp/index.html /usr/share/nginx/html/
sudo mv /tmp/photo.jpg /usr/share/nginx/html/

# Set correct file permissions
sudo chmod 644 /usr/share/nginx/html/index.html
sudo chmod 644 /usr/share/nginx/html/photo.jpg

# Verify nginx status
sudo systemctl status nginx
```

## 3. Access the application
Open a browser and navigate to `http://<EC2_PUBLIC_IPV4>`
