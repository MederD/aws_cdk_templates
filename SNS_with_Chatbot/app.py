#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_sns.cdk_sns_stack import CdkSnsStack
from aws_cdk import (Tags, Stack)

app = cdk.App()

CdkSnsStack(app, "YOUR-STACK-NAME",
    description="This stack will create SNS Topic and chatbot configuration",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
    )

# Add tags to all constructs in the stack
Tags.of(app).add("tag1", "value1")
Tags.of(app).add("tag2", "value2")
Tags.of(app).add("tag3", "value3")
Tags.of(app).add("tag4", "value4")
Tags.of(app).add("tag5", "value5")

app.synth()
