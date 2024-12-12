# Lambda-3100
AWS Lambda Secure Card Transaction System

Project Overview

This project implements a serverless AWS Lambda function designed to facilitate secure card transactions between retailers and banks. The system uses AWS services such as DynamoDB, S3, and API Gateway to handle transaction data securely and efficiently.

Key Features:
Secure Transaction Processing: Ensures privacy through encryption and compliance with industry standards.
Serverless Architecture: Utilizes AWS Lambda for scalability and cost efficiency.
Efficient Data Handling: Leverages DynamoDB for fast, low-latency data storage, and S3 for secure, encrypted file storage.
CI/CD Automation: Integrated CI/CD pipeline to automate updates and deployment processes.
Architecture Diagram


A simple diagram to visualize the architecture can be added here.

Technologies Used:

AWS Lambda – Serverless compute service to execute the transaction processing logic.
AWS DynamoDB – NoSQL database for storing transaction metadata and details.
AWS S3 – Object storage service used to securely store encrypted transaction data.
AWS API Gateway – Manages and routes API requests between the retailers and the Lambda function.
AWS CloudFormation – For deploying and managing AWS resources in a repeatable and automated way.
AWS IAM – Role-based access control for securing AWS resources.
