# AWS CDK Deployment Guide

This guide will walk you through the process of deploying an AWS CloudFormation stack using the AWS Cloud Development Kit (CDK) with a specific profile.

## Prerequisites

AWS CDK is [installed](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) on your local machine.   
[Bootstraped](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)  
You have created an AWS profile with the necessary permissions to deploy CloudFormation stacks.

## Steps

Follow the steps from [CDK Developer Guide](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html)  
Copy the contents of the files from this repository.  
Open a command-line terminal and run the following command to initialize your CDK app:  
Once the initialization is complete, you can run the following command to deploy your stack:  

```bash
cdk deploy StackName --profile profileName
```

Replace StackName with the name of your CloudFormation stack and profileName with the name of the AWS profile you created in the prerequisites.  

The CDK will prompt you to confirm the deployment. Enter "y" to confirm.  

The deployment process will take a few minutes to complete. Once it finishes, the CDK will display the outputs of your stack, which can be used to access any resources created by your stack.  

### Congratulations! You have successfully deployed your AWS CDK stack using a specific profile
