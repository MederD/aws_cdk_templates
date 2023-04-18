import boto3
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_exception(e):
    """
    Logs an error and sends an SNS notification.

    Args:
        e: The exception object.

    Returns:
        None.
    """
    sns = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    account_id = os.environ['AWS_ACCOUNT_ID']
    log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']

    logger.error(f'An error occurred: {e}')
    construct_message = f":rotating-light-red: Lambda: {function_name}, in account: {account_id} has failed, check the log: {log_group_name}"
    sns.publish(
        TargetArn=sns_topic_arn,
        Message=construct_message,
        Subject='--- LAMBDA FAILURE ---'
    )
