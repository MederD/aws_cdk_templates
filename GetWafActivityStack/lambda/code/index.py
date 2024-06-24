import boto3
from log_wrapper import LogWrapper
from secret_wrapper import SecretsWrapper
from waf_wrapper import WAFWrapper
import requests
import os

# Environment variables
sns_topic = os.environ['sns_topic']
secretname = os.environ['secretname']
logName = os.environ['logGroupName']
query_string = os.environ['query']
ip_set_name = os.environ['ip_set_name']
ip_set_id = os.environ['ip_set_id']

# Create clients and wrappers
def create_clients_and_wrappers():
    waf_client = boto3.client('wafv2', region_name = 'us-east-1')
    log_client = boto3.client('logs', region_name = 'us-east-1')
    secret_client = boto3.client('secretsmanager', region_name = 'us-east-1')
    client_sns = boto3.client('sns', region_name = 'us-east-1')

    waf_wrapper = WAFWrapper(waf_client)
    log_wrapper = LogWrapper(log_client)
    secret_wrapper = SecretsWrapper(secret_client)

    return waf_wrapper, log_wrapper, secret_wrapper, client_sns

waf_wrapper, log_wrapper, secret_wrapper, client_sns = create_clients_and_wrappers()

def handler(event, context):
    try:
      virustotal_api_key = secret_wrapper.get_secrets(secretname)

      ips = log_wrapper.query_logs(logName, query_string)
      log_wrapper.logger.info(" --- Will check this IPs %s. --- ", ips )
      
      if not ips:
         log_wrapper.logger.info(" --- No results to proceed --- ")
         return
      
      # Get the Virus Total report
      for ip in ips:
        response = requests.get(
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
            headers={
                'x-apikey': virustotal_api_key['virustotalkey']
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
                    TargetArn = sns_topic,
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
      
      # If same CIDR ips are found add them to IP set
      same_cidr_ips = waf_wrapper.get_same_cidr_ips(ips)
      log_wrapper.logger.info(" --- Detected IPs within same CIDR %s. --- ", same_cidr_ips )
      
      if not same_cidr_ips:
          log_wrapper.logger.info(" --- No IPs with the same CIDR found ---")
      else:
        for ip in same_cidr_ips:
            if ip_set_id is not None:
                message = ":rotating-light-red: Detected IPs within same CIDR: %s" % (same_cidr_ips)       
                client_sns.publish(
                    TargetArn = sns_topic,
                    Message = message,
                    Subject = 'Log query results'
                )
                addresses, lock_token = waf_wrapper.check_ip_in_waf(ip, ip_set_id, ip_set_name, scope='CLOUDFRONT')
                if ip not in addresses:
                    addresses.append(ip+'/24')
                    log_wrapper.logger.info(f" --- New IP set addresses {addresses} ---")
                    log_wrapper.logger.info(f" --- Adding {ip + '/24'} to the IP set {ip_set_name} ---")
                    waf_wrapper.add_ip_to_waf(addresses, ip_set_id, lock_token, ip_set_name, scope='CLOUDFRONT')
                else:
                    log_wrapper.logger.info(f" --- {ip} exists in the IP set ---")
            else:
                log_wrapper.logger.info(" --- No IP set found --- ")

    except Exception as e:
        log_wrapper.logger.error(" --- Error: %s --- ", str(e))
        raise
