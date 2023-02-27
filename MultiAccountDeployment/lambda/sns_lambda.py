import urllib3
import json, os, logging

# logging configuration
logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

http = urllib3.PoolManager()

# environment variables
env_url = os.environ['slack_url']
logger.info("Slack url: %s.", env_url)

def handler(event, context):
  url = env_url
  msg = {
    "text": event['Records'][0]['Sns']['Message']
  }
  logger.info("Constructing message %s.", msg)
  encoded_msg = json.dumps(msg).encode('utf-8')
  try:
    resp = http.request('POST',url, body=encoded_msg)
  except Exception as error:
    logger.error(error)
