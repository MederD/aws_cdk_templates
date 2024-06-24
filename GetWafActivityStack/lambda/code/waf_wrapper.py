import boto3
from collections import Counter

class WAFWrapper:
    def __init__(self, waf_client):
        self.waf_client = waf_client

    @classmethod
    def from_resource(cls):
        waf_client = boto3.client('wafv2')
        return cls(waf_client)

    def get_cidr(self, ip):
        return ".".join(ip.split(".")[:3])

    def get_same_cidr_ips(self, ips):
        cidrs = [self.get_cidr(ip) for ip in ips]
        counter = Counter(cidrs)
        same_cidr_ips = [ip + ".0" for ip, count in counter.items() if count > 3]
        return same_cidr_ips
    
    def get_ip_set_id(self, name, scope='CLOUDFRONT'):
        response = self.waf_client.list_ip_sets(Scope=scope)
        for ip_set in response['IPSets']:
            if ip_set['Name'] == name:
                return ip_set['Id']
        return None

    def check_ip_in_waf(self, ip, ip_set_id, name, scope='CLOUDFRONT'):
        response = self.waf_client.get_ip_set(Id=ip_set_id, Name=name, Scope=scope)
        return response['IPSet']['Addresses'], response['LockToken']

    def add_ip_to_waf(self, addresses, ip_set_id, lock_token, name, scope='CLOUDFRONT'):
        self.waf_client.update_ip_set(
            Name=name,
            Scope=scope,
            Id=ip_set_id,
            Addresses=addresses,
            LockToken=lock_token
        )
