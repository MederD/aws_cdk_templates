#!/usr/bin/env python3
import os
import aws_cdk as cdk
from server_automation.server_automation_stack import ServerAutomationStack
from aws_cdk import (Tags)


app = cdk.App()

Stack = ServerAutomationStack(app, "Stack",
    stack_name = "ScheduleInstances-Stack",
    description = "A stack that deploys a Lambda function and two scheduled CloudWatch Events to start and stop EC2 instances.",
    env = cdk.Environment(account = os.environ["CDK_DEFAULT_ACCOUNT"], region = os.environ["CDK_DEFAULT_REGION"])
    )
Tags.of(Stack).add("key","value")

# Add a tag to all constructs in the stack
tags = {'key1': 'value1', 'key2':'value2'}
for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
