#!/usr/bin/env python3
import os
import aws_cdk as cdk
from remove_unused_policies.remove_unused_policies_stack import RemoveUnusedPoliciesStack
from aws_cdk import (Tags)


app = cdk.App()

DevStack = RemoveUnusedPoliciesStack(app, "RemoveUnusedPoliciesStack",
    stack_name = "RemoveUnusedPoliciesStack",
    description = "A stack that deploys a Lambda function and CloudWatch Events rule to track unused IAM policies.",
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
    )

Tags.of(DevStack).add("key","value")

# Add a tag to all constructs in the stack
tags = {"key1": "value1"}
for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
