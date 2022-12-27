#!/usr/bin/env python3
import os
import aws_cdk as cdk
from get_update.get_update_stack import GetUpdateStack
from aws_cdk import (Tags, Stack)

app = cdk.App()

GetUpdateStack(app, "STACK-NAME",
    description="STACK-DESCRIPTION",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
    )

# Add a tag to all constructs in the stack
tags = {'Key1': 'Value1', 'Key2': 'Value2', 'Key3':'Value3'}
for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
