import boto3
from log_wrapper import LogWrapper
import requests
import os

secretsmanager = boto3.client('secretsmanager')
client_sns = boto3.client('sns')
sns_topic = os.environ['sns_topic']
secretname = os.environ['secretname']
logName = os.environ['logGroupName']
query_string = os.environ['query']

log_wrapper = LogWrapper(log_client = boto3.client('logs', region_name = 'us-east-1'))

# Retrieve the secret value
response = secretsmanager.get_secret_value(SecretId = secretname)
vt_api = response['SecretString']

def handler(event, context):
    try:
      topic = sns_topic
      ips = log_wrapper.query_logs(logName, query_string)
      log_wrapper.logger.info(" --- Will check this IPs %s. --- ", ips )

      if not ips:
         log_wrapper.logger.info(" --- No results to proceed --- ")
         return

      for ip in ips:
        response = requests.get(
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
            headers={
                'x-apikey': vt_api
            }
        )

        if response.status_code == 200:
            data = response.json()['data']
            malicious = data['attributes']['last_analysis_stats']['malicious']
            suspicious = data['attributes']['last_analysis_stats']['suspicious']

            if malicious > 0 or suspicious > 0:
                message = {
                    "ip": data['id'],
                    "malicious": malicious,
                    "suspicious": suspicious
                }

            log_wrapper.logger.info(" --- Constructing message %s. --- ", message)
        
            client_sns.publish(
                TargetArn = topic,
                Message = message,
                Subject = 'Log query results'
            )
        
        else:
            log_wrapper.logger.info(" --- No recorded malicious or suspicious report on virustotal of IP: %s. --- ", ip)  

    except Exception:
        log_wrapper.logger.error(" --- Error! --- ")
        raise
