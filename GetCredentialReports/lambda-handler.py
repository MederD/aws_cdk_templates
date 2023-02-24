import boto3
from botocore.exceptions import ClientError
import os
import csv, codecs
from time import sleep
import datetime
import dateutil.parser
import logging

logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

# set local testing configuration
LOCAL_TESTING = False

if LOCAL_TESTING:
    session = boto3.Session(profile_name = 'your-profile')
    iam_client = session.client('iam', region_name = 'your-region')
    sns_topic = 'some-sns-topic'
else:
    client_sns = boto3.client('sns')
    iam_client = boto3.client('iam')
    sns_topic = os.environ['sns_topic']

def days_till_expire(last_changed, max_age):
    if type(last_changed) is str:
        last_changed_date=dateutil.parser.parse(last_changed).date()
    elif type(last_changed) is datetime.datetime:
        last_changed_date=last_changed.date()
    else:
        return -99999
    expires = (last_changed_date + datetime.timedelta(max_age)) - datetime.date.today()
    return(expires.days)

def get_credential_report(iam_client):
    resp1 = iam_client.generate_credential_report()
    if resp1['State'] == 'COMPLETE' :
        try: 
            response = iam_client.get_credential_report()
            credential_report_csv = response['Content']
            reader = csv.DictReader(codecs.iterdecode(credential_report_csv.splitlines(), 'utf-8'))
            credential_report = {}
            for row in reader:
                key = row['user']
                credential_report[key] = row
            return(credential_report)
        except ClientError as e:
            logger.exception(e)
            print("Unknown error getting Report: " + e.message)
    else:
        sleep(2)
        return get_credential_report(iam_client)

def get_max_password_age(iam_client):
    try: 
        response = iam_client.get_account_password_policy()
        return response['PasswordPolicy']['MaxPasswordAge']
    except ClientError as e:
        logger.exception(e)
        print("Unexpected error in get_max_password_age: %s" + e.message) 

if LOCAL_TESTING:
    logger.info("Local testing: {}".format(LOCAL_TESTING))
    logger.info("SNSTopic: {}".format(sns_topic))

    def main(): 
        try:
            max_age = get_max_password_age(iam_client)
            credential_report = get_credential_report(iam_client)
            for user in credential_report:
                if credential_report[user]['password_enabled'] != 'true':
                    logger.info("Skipping service users: {}".format(user))
                else:
                    message = ""
                    password_expires = days_till_expire(credential_report[user]['password_last_changed'], max_age)
                    if password_expires > 0:
                        message = "Password expires for user: {}".format(user) + " in: " + (format(abs(password_expires * -1))) + " days"
                        logger.info(message)
                    elif password_expires < 90 :
                        message = "ATTENTION! Password expired for user: {}".format(user) + ": " + format(password_expires * -1) + " days ago"
                        logger.info(message)
        except ClientError as e:
            logger.exception(e)

    main()

else:
    logger.info("Local testing: {}".format(LOCAL_TESTING))
    logger.info("SNSTopic: {}".format(sns_topic))

    def handler(event, context): 
        try:
            max_age = get_max_password_age(iam_client)
            credential_report = get_credential_report(iam_client)
            for user in credential_report:
                if credential_report[user]['password_enabled'] != 'true':
                    logger.info("Skipping service users: {}".format(user))
                else:
                    message = ""
                    password_expires = days_till_expire(credential_report[user]['password_last_changed'], max_age)
                    if password_expires > 0:
                        message = "Password expires for user: {}".format(user) + " in: " + (format(abs(password_expires * -1))) + " days"
                        client_sns.publish(
                            TargetArn = sns_topic,
                            Message = message,
                            Subject = '--- PASSWORD EXPIRATION REPORT ---'
                        )
                    elif password_expires < 90 :
                        message = "ATTENTION! Password expired for user: {}".format(user) + ": " + format(password_expires * -1) + " days ago"
                        client_sns.publish(
                            TargetArn = sns_topic,
                            Message = message,
                            Subject = '--- PASSWORD EXPIRATION REPORT ---'
                        )
        except ClientError as e:
            logger.exception(e)



