#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (Tags)
from get_waf_activity.get_waf_activity_stack import GetWafActivityStack


app = cdk.App()

GetWafActivityStack(app, "GetWafActivityStack",
    stack_name = "GetWafActivityStack",
    description = "This stack will create WAF activity report and send to slack channel"
    )

# Add a tag to all constructs in the stack
tags = {'Name': 'MCW-GetWafActivityStack', 
        'Service':'AWSSecurity', 
        'CreatedWith':'AWS CDK', 
        'AccountNumber':'607525',
        'CreatedBy':'Med'}

for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
