# Find Idle Instances in AWS EC2 Using AWS CDK and Python 

This project provides a solution to find idle EC2 instances in an AWS account using AWS Cloud Development Kit (CDK) and Python. The solution uses a combination of AWS Lambda, Amazon CloudWatch Events, and Amazon Simple Notification Service (SNS) to generate and send reports of idle instances to a specified SNS topic.  

## Requirements

    Python 3.8 or later
    Node.js 14 or later
    AWS CDK version 1.130.0 or later

## Installation

1. Clone this repository to your local machine.
2. Change into the find_idle_instances directory.
3. Install the required Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Install the required Node.js dependencies:
    ```sh
    npm install
    ```
    
## Configuration

Create an SNS topic to receive the reports. Note the ARN of the topic.

Configure the Lambda function with the necessary IAM permissions and the ARN of the SNS topic.

Set the environment variables in the Lambda function:

   - PERIOD: the length of the time interval to check for idle instances in seconds (default: 3600).
   - REGION: the AWS region where the EC2 instances are located (default: us-west-2).
   - METRICS: a comma-separated list of the EC2 instance metrics to include in the report (default: "CPUUtilization,NetworkPacketsIn,NetworkPacketsOut").

Create a CloudWatch Events rule to trigger the Lambda function on a schedule.

The report will be sent to the configured SNS topic if any idle instances are found.

## Deploying the stack

To deploy the stack, run the following command:
```sh
cdk deploy
```
This will deploy the stack with the default parameters. You can also provide your own parameters by editing the cdk.json file.

## Usage
When the stack is deployed, it will create a Lambda function and a CloudWatch event rule that triggers the function every day at 8:00 PM UTC. The Lambda function will find any idle instances between the start time and end time (specified in the cdk.json file) and send a report to the SNS topic.
Modifying the stack

If you want to modify the stack, you can do so by editing the get_idle_instances_stack.py file. This file contains the stack definition, which includes the Lambda function, CloudWatch event rule, and SNS topic.

The report will be in the following format:

```php

Idle instance found: <instance_id> between <start_time> and <end_time>
<timestamp> - Average CPU: <cpu_utilization>%, NetworkPacketsIn: <network_packets_in>, NetworkPacketsOut: <network_packets_out>
```
Where:

    - <instance_id> is the ID of the idle instance
    - <start_time> and <end_time> are the start and end times of the check interval
    - <timestamp> is the timestamp of the performance metrics
    - <cpu_utilization> is the average CPU utilization during the interval
    - <network_packets_in> is the number of incoming network packets during the interval
    - <network_packets_out> is the number of outgoing network packets during the interval

## Cleaning up

To delete the stack and all the resources created by it, run the following command:
```sh
cdk destroy
```
