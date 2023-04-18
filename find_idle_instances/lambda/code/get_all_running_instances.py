import logging
import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_all_running_instances():
    """
    Retrieves all running EC2 instances.

    Returns:
        A list of running EC2 instances.
    """
    try:
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        return instances
    except Exception as e:
        logger.error(f"An error occurred while retrieving running EC2 instances: {e}")
        raise e
