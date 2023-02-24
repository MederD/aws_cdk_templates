#!/usr/bin/env python3
import os
import aws_cdk as cdk
from get_credential_reports.get_credential_reports_stack import GetCredentialReportsStack
from aws_cdk import (Tags)


app = cdk.App()

GetCredentialReportsStack(app, "GetCredentialReportsStack",
    description="This stack will create cron job and lambda function",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
    )

# Add a tag to all constructs in the stack
tags = {'Key1': 'Value1', 'Key2': 'Value2'}
for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
