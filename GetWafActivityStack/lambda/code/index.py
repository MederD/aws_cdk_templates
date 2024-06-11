import boto3
from log_wrapper import LogWrapper
from secret_wrapper import SecretsWrapper
import requests
import os

client_sns = boto3.client('sns')
sns_topic = os.environ['sns_topic']
secretname = os.environ['secretname']
logName = os.environ['logGroupName']
query_string = os.environ['query']

log_wrapper = LogWrapper(log_client = boto3.client('logs', region_name = 'us-east-1'))
secret_wrapper = SecretsWrapper(secret_client = boto3.client('secretsmanager', region_name = 'us-east-1'))
vt_api = secret_wrapper.get_secrets(secretname)

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
                'x-apikey': vt_api['virustotalkey']
            }
        )

        if response.status_code == 200:
            data = response.json()['data']
            malicious = data['attributes']['last_analysis_stats']['malicious']
            suspicious = data['attributes']['last_analysis_stats']['suspicious']

            log_wrapper.logger.info("%s report -> malicious: %s, suspicious: %s", data['id'], malicious, suspicious)

            if malicious > 1 or suspicious > 1:
                message = "IP: %s, Malicious: %s, Suspicious: %s" % (data['id'], malicious, suspicious)
                
                log_wrapper.logger.info(" --- Constructing message for %s --- ", data['id'])
        
                client_sns.publish(
                    TargetArn = topic,
                    Message = message,
                    Subject = 'Log query results'
                )
        
            else:
                log_wrapper.logger.info(" --- No recorded malicious or suspicious report on virustotal of IP: %s. --- ", ip)  
        else:
            try:
                error_message = response.json()['error']['message']
                log_wrapper.logger.info(error_message)
            except Exception as e:
                log_wrapper.logger.info(f"Failed to get error message from response: {e}")

    except Exception:
        log_wrapper.logger.error(" --- Error! --- ")
        raise
