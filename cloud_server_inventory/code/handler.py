import os
import logging
import boto3, time
from getservers import InstanceWrapper

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)

account_id = os.environ['account_id']
role_assume = os.environ['assumed_role']
tablename = os.environ['tablename']

if account_id != 'SOME-ACCOUNT-ID':
    region = 'us-west-2'
else:
    region = 'us-east-1'

sts_client = boto3.client('sts')
sts_session = sts_client.assume_role(RoleArn = role_assume, 
                                     RoleSessionName = 'dynamodb-session')
KEY_ID = sts_session['Credentials']['AccessKeyId']
ACCESS_KEY = sts_session['Credentials']['SecretAccessKey']
TOKEN = sts_session['Credentials']['SessionToken']

def handler(event, context):
    time.sleep(15)
    ec2_client = boto3.client('ec2', region_name = region)
    instance_wrapper = InstanceWrapper(ec2_client, account_id)
    dynamodb_client = boto3.client('dynamodb',
        region_name = region, 
        aws_access_key_id = KEY_ID, 
        aws_secret_access_key = ACCESS_KEY, 
        aws_session_token = TOKEN)
    try:
        # Retrieve all running and stopped instances in this account
        instances = instance_wrapper.get_all_instances(account_id)
        
        # Retrieve existing DynamoDB items
        response = dynamodb_client.scan(
            TableName=tablename,
            FilterExpression='Account = :a',
            ExpressionAttributeValues={
                ':a': {
                    "S": account_id}
                }
            ) 
        dynamodb_items = response.get('Items', [])

        # Create a set of existing instance IDs
        existing_dynamodb_items = set(item['InstanceId']['S'] for item in dynamodb_items)
            
        for ids in instances:
            if ids not in existing_dynamodb_items:
                # Convert datetime to string first
                LaunchDate = instances[ids]['LaunchDate'].strftime("%m/%d/%Y")
            
                dynamodb_client.put_item(
                    TableName = tablename,
                    Item = {
                        "InstanceId": {'S': ids},
                        "Account": {'S': instances[ids]['Account']},
                        "Type": {'S': instances[ids]['Type']},
                        "LaunchDate": {'S': LaunchDate},
                        "Platform": {'S': instances[ids]['Platform']},
                        "PrivateIp": {'S': instances[ids]['PrivateIp']},
                        "PuplicIp": {'S': instances[ids]['PublicIp']},
                        "State": {'S': instances[ids]['State']}
                    })
                logger.info(f"Inserted new DynamoDB item for instance ID: {ids}")
                
        #Delete items not associated with EC2 instances
        for item in existing_dynamodb_items:
            if item not in instances:
                logger.info(f"Item: {item} needs to be deleted...")
                
                dynamodb_client.delete_item(
                    TableName = tablename, 
                    Key={
                        "InstanceId": {"S": item},
                        "Account": {"S": account_id}
                        }
                    )
                logger.info(f"Deleted DynamoDB item for instance ID: {item}")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
