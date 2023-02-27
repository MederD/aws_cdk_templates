#!/usr/bin/env python3
import os
import aws_cdk as cdk
from get_credential_report.get_credential_report_stack import GetCredentialReportStack
from aws_cdk import (Tags)


app = cdk.App()

DevStack = GetCredentialReportStack(app, "DevStack",
    stack_name = "GetCredentialReportDevStack",
    description="This stack will create credential report and send to slack channel",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
    )

TestStack = GetCredentialReportStack(app, "TestStack",
    stack_name = "GetCredentialReportTestStack",
    description="This stack will create credential report and send to slack channel",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
    )

ProdStack = GetCredentialReportStack(app, "ProdStack",
    stack_name = "GetCredentialReportProdStack",
    description="This stack will create credential report and send to slack channel",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
    )

Tags.of(DevStack).add("Environment","Dev")
Tags.of(TestStack).add("Environment","Test")
Tags.of(ProdStack).add("Environment","Prod")

# Add a tag to all constructs in the stack
tags = {'key1': 'value1', 'key2':'value2'}
for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
