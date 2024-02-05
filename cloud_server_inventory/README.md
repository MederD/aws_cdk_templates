# Multi-Account DynamoDB Access with AWS CDK
This repository contains an AWS Cloud Development Kit (CDK) project that sets up a DynamoDB table, deploys a Lambda function, and manages the required IAM roles. The project is organized into two stacks:

## Stack 1 (Full Deployment)

Creates a DynamoDB table.
Deploys a Lambda function.
Sets up the necessary IAM roles for both the DynamoDB table and Lambda function.
Allows multi-account access to the DynamoDB table.

## Stack 2 (Lambda-Only Deployment)

Deploys only the Lambda function.
Assumes the IAM role created in Stack 1 for DynamoDB access.

## Prerequisites
Before you begin, ensure you have the following prerequisites:

1. **AWS CLI and AWS CDK**: Make sure you have the AWS Command Line Interface (CLI) and AWS CDK installed on your local machine.

2. **AWS Account Setup**: Set up your AWS account and configure your credentials using the AWS CLI.

## Getting Started
1. Clone this repository to your local machine:
2. Install dependencies:
```
npm install
```
3. Review the "app.py" examples and customize them according to your use case.
4. Explore the "cloud_server_inventory_stack.py" file. This stack defines the infrastructure components using AWS CDK constructs.

## Deploying the Stacks
Stack 1: Full Deployment
Deploy Stack 1 (DynamoDB, Lambda, and IAM roles):
``
cdk deploy Stack1
``
This will create the DynamoDB table, deploy the Lambda function, and set up the necessary IAM roles.

Stack 2: Lambda-Only Deployment
Deploy Stack 2 (Lambda function and IAM role):
``
cdk deploy Stack2
``
Stack 2 assumes the IAM role created in Stack 1, allowing the Lambda function to access the DynamoDB table.

## CodePipeline Integration
The repository includes a "buildspec.yaml" file for use with AWS CodePipeline. Set up a CodePipeline to automatically build and deploy your stacks whenever changes are pushed to the repository. Pipeline templates are also given as an example.

## Cleanup
To remove the deployed resources, run:
``
cdk destroy
``
## Additional Notes
Ensure that your AWS credentials are properly configured before deploying the stacks.
Customize the stack names, resource names, and other parameters as needed.
