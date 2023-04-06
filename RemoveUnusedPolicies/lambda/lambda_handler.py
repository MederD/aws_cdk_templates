import boto3
import logging
import os

# Initialize the AWS SDK clients
iam = boto3.resource('iam')
client_sns = boto3.client('sns')

# Configure logging
logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))
  
def list_policies(scope = 'All'):
    """
    Lists the policies in the current account.

    :param scope: Limits the kinds of policies that are returned. For example,
                  'Local' specifies that only locally managed policies are returned.
    :return: The list of policies, or None if an error occurs.
    """
    try:
        # Use the IAM resource to list the policies with the specified scope
        policies = list(iam.policies.filter(
                        Scope = scope,
                        MaxItems = 120
                        ))
        
        # Log the number of policies retrieved
        logger.info("Got %s policies in scope '%s'.", len(policies), scope)

        # Return the list of policies
        return policies
    
    except Exception as e:
        logger.exception(e)
        return None

def delete_policy(policy):
    """
    Deletes the specified policy.

    :param policy: The policy to delete.
    """
    try:
        # Delete all versions of the policy except for the default version
        for version in policy.versions.all():
            if not version.is_default_version:
                version.delete()
                logger.info("Deleted policy version '%s'.", version.version_id)

        # Delete the policy and log a success message
        policy.delete()
        logger.info("Policy '%s' deleted.", policy.arn)
    
    except Exception as e:
        logger.error(f"Couldn't delete policy '%s': {e}", policy.arn)
        logger.exception(e)

def check_and_delete_policies(policies):
    """
    Checks for attachments on each policy and deletes any policies with no attachments.

    :param policies: The list of policies to check and delete.
    """
    try:
        for policy in policies:
            # Use the policy ARN to get the policy object
            policy_obj = iam.Policy(policy.arn)
            # Check if the policy has any attachments
            if not policy_obj.attachment_count:
                logger.info("Policy '%s' has no attachments and will be deleted.", policy.arn)
                # If the policy has no attachments, delete it
                delete_policy(policy_obj)
            else:
                logger.info("Policy '%s' has %d attachments and will not be deleted.", policy.arn, policy_obj.attachment_count)
    except Exception as e:
        logger.exception(e)

""" Global variables """
account_id = os.environ["AccountId"]
function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']
sns_topic = os.environ['sns_topic']
function_region = os.environ['AWS_REGION']

def handle_exception(e):
    """
    Handles exceptions by logging the error and sending a message to an SNS topic.

    :param e: The exception to handle.
    """
    logger.error(f'An error occurred: {e}')
    construct_message = f":rotating-light-red: Lambda: {function_name}, in account: {account_id} has failed, check the log: {log_group_name}"
    client_sns.publish(
        TargetArn = sns_topic,
        Message = construct_message,
        Subject = '--- LAMBDA FAILURE ---'
    )

def lambda_handler(event, context):
    try:
        # List policies with no attachments
        policies = list_policies(scope = 'Local')
        # Check for attachments and delete policies with
        check_and_delete_policies(policies)
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        handle_exception(e)
