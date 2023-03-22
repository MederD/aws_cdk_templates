"""
Description: This Lambda function is triggered by an EventBridge rule and checks whether EC2 instances tagged with
             'Scheduled = True' are running or stopped. If an instance is stopped, it starts it and waits for it to be
             in the running state. If an instance is running, it stops it and waits for it to be in the stopped state.
             The function uses the InstanceWrapper class from the instance_wrapper module to interact with the EC2 API.
"""

import boto3, os, logging
from instance_wrapper import InstanceWrapper

""" configure logging """ 
logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))


def handler(event, context):
    """
    Function that is executed when the Lambda function is triggered.

    :param event: The event that triggered the function
    :param context: The context in which the function is executing
    """
    ec2_client = boto3.client('ec2')
    instance_wrapper = InstanceWrapper(ec2_client)

    filters = [{'Name': 'tag:Scheduled', 'Values': ['True']}]
    logger.info(f'Filters set to: {filters}')

    instances = instance_wrapper.filter_instances(filters)
    for instance in instances:
        instance_id = instance['InstanceId']
        instance_state = instance['State']['Name']
    logger.info(f'InstanceId - {instance_id}, state {instance_state}')
    try:
        if instance_state == 'stopped':
            instance_wrapper.start_instance(instance_id)
            status = instance_wrapper.describe_instance_status(instance_id)
            if status == 'running':
                logger.info(f'Success. Instance {instance_id} is {status}')
            else:
                logger.info('Instance not in RUNNING state, yet')
     
        elif instance_state == 'running':
            instance_wrapper.stop_instance(instance_id)
            status = instance_wrapper.describe_instance_status(instance_id)
            if status == 'stopped':
                logger.info(f'Success. Instance {instance_id} is {status}')
            else:
                logger.info('Instance not in STOPPED state, yet')
    except Exception as error:
        logger.exception(error)
        raise

