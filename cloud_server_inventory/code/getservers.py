import logging
import boto3
import collections

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)

class InstanceWrapper:
    def __init__(self, ec2_client, instance = None):
        self.ec2_client = ec2_client
        self.instance = instance

    @classmethod
    def from_resource(cls):
        ec2_client = boto3.client('ec2')
        return cls(ec2_client)
    
    def get_all_instances(self, account_id):
        try:
            instance_l = collections.defaultdict(dict)
            response = self.ec2_client.describe_instances(MaxResults = 100)
            for object in response['Reservations']:
                for instance in object['Instances']:
                    if instance['State']['Name'] != 'terminated':
                        instance_l[instance['InstanceId']]['Account'] = account_id
                        instance_l[instance['InstanceId']]['Type'] = instance['InstanceType']
                        instance_l[instance['InstanceId']]['LaunchDate'] = instance['LaunchTime'].date()
                        instance_l[instance['InstanceId']]['Platform'] = instance['PlatformDetails']
                        instance_l[instance['InstanceId']]['PrivateIp'] = instance['PrivateIpAddress']
                        instance_l[instance['InstanceId']]['State'] = instance['State']['Name']
                        if 'PublicIpAddress' in instance:
                            instance_l[instance['InstanceId']]['PublicIp'] = instance['PrivateIpAddress']
                        else:
                            instance_l[instance['InstanceId']]['PublicIp'] = 'None'
                        # logger.info(f"InstanceId: {instance['InstanceId']}, InstanceType: {instance['InstanceType']}, LaunchDate: {instance['LaunchTime'].date()}, Platform: {instance['PlatformDetails']}, PrivateIp: {instance['PrivateIpAddress']}\n")
        
            return instance_l
        except Exception as e:
            logger.error(f"An error occurred while retrieving EC2 instances: {e}")
            raise e
