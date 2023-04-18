#!/usr/bin/env python3
import os
import aws_cdk as cdk
from find_idle_instances.find_idle_instances_stack import FindIdleInstancesStack
from aws_cdk import (Tags)

app = cdk.App()
Stack = FindIdleInstancesStack(app, "FindIdleInstancesStack",
                                stack_name = "FindIdleInstancesStack",
                                description=(
                                    "The FindIdleInstancesStack is an AWS CDK stack that automates the process of "
                                    "identifying idle EC2 instances based on specified metric thresholds.\n\n"
                                ),
                                env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
                                )

Tags.of(Stack).add("key","value")

# Add a tag to all constructs in the stack
tags = {'Name': 'FindIdleInstancesStack'}
for key, value in tags.items():
    Tags.of(app).add(key, value)
    
app.synth()
