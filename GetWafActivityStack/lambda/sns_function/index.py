import urllib3
import json, os, logging

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()
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
    logger.info(
        'message: %s, status_code: %s, response: %s',
        event['Records'][0]['Sns']['Message'],
        resp.status,
        resp.data
)
  except Exception:
    logger.error("Error")
    raise
