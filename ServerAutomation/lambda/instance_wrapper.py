"""
Description: This code defines a class called InstanceWrapper which is used to interact with EC2 instances in AWS. 
             The class has several methods to perform operations like filtering instances based on tags, starting/stopping instances, 
             and getting the status of an instance.
"""

import boto3, os, logging

""" configure logging """ 
logger = logging.getLogger()
logging.basicConfig(
    format = "[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", 
    datefmt = "%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

class InstanceWrapper:
    """
    The class has an init() method which initializes the class with an EC2 client object and an instance object if provided.
    """
    def __init__(self, ec2_client, instance = None):
        """
        Constructor method for InstanceWrapper class.
        :param ec2_client: Boto3 EC2 client object.
        :param instance: Instance object.
        """
        self.ec2_client = ec2_client
        self.instance = instance

    @classmethod
    def from_resource(cls):
        """
        The class method from_resource() creates an instance of the class with an EC2 client object.
        :return: InstanceWrapper object.
        """
        ec2_client = boto3.client('ec2')
        return cls(ec2_client)

    def filter_instances(self, filters):
        """
        The method filter_instances() filters EC2 instances based on tags using the describe_instances() method of the EC2 client. 
        The method returns a list of instances that match the given filters.
        :param filters: A list of dictionaries containing the filter criteria.
        :return: A list of EC2 instance objects that match the given filters.
        """
        try:
            response = self.ec2_client.describe_instances(Filters = filters)
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(instance)
            return instances
        except Exception as error:
            logger.exception(error)
            raise

    def start_instance(self, instance_id):
        """
        The start_instance() method starts the given EC2 instance using the start_instances() method of the EC2 client. 
        The method then waits until the instance is in the 'running' state using a waiter object returned by get_waiter() method of the EC2 client. 
        The method raises an exception if the instance does not enter the 'running' state within a specified number of attempts and delay time.
        :param instance_id: The ID of the instance to start.
        """
        try:
            self.ec2_client.start_instances(InstanceIds = [instance_id])
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter_config = {'Delay': 10, 'MaxAttempts': 3}
            waiter.wait(InstanceIds = [instance_id], WaiterConfig = waiter_config)
            logger.info(f"Started instances {instance_id}")
        except Exception as error:
            logger.exception(error)
            raise

    def stop_instance(self, instance_id):
        """
        The stop_instance() method stops the given EC2 instance using the stop_instances() method of the EC2 client. 
        The method then waits until the instance is in the 'stopped' state using a waiter object returned by the get_waiter() method of the EC2 client. 
        The method raises an exception if the instance does not enter the 'stopped' state within a specified number of attempts and delay time.
        :param instance_id: The ID of the instance to stop.
        """
        try:
            self.ec2_client.stop_instances(InstanceIds = [instance_id])
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter_config = {'Delay': 10, 'MaxAttempts': 3}
            waiter.wait(InstanceIds = [instance_id], WaiterConfig = waiter_config)
            logger.info(f"Stopped instances {instance_id}")
        except Exception as error:
            logger.exception(error)
            raise

    def describe_instance_status(self, instance_id):
        """
        The describe_instance_status() method gets the status of the given EC2 instance using the describe_instance_status() method of the EC2 client. 
        The method returns the state of the instance as a string.
        :param instance_id: The ID of the instance to get the status of.
        :return: The status of the instance.
        """
        try:
            response = self.ec2_client.describe_instance_status(
                InstanceIds = [instance_id],
                IncludeAllInstances = True
            )
            status = response['InstanceStatuses'][0]['InstanceState']['Name']
            return status
        except Exception as error:
            logger.exception(error)
            raise

   


