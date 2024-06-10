import boto3, json

class SecretsWrapper:
    def __init__(self, secret_client, instance = None):
        self.secret_client = secret_client
        self.instance = instance

    @classmethod
    def from_resource(cls):
        secret_client = boto3.client('secretsmanager')
        return cls(secret_client)

    def get_secrets(self, secretId):
        try:
            _secret = json.loads(self.secret_client.get_secret_value(SecretId = secretId)['SecretString'])
            return _secret
        
        except Exception as e:
            raise e
