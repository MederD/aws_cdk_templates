#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (Tags)
from cloud_server_inventory.cloud_server_inventory_stack import CloudServerInventoryStack

app = cdk.App()

Stack1 = CloudServerInventoryStack(app, "Dev",
        stack_name = "CloudServerInventoryStack",
        description = "This stack will create DynamoDB, lambda function and IAM roles",
        build_table = True
        )

Stack2 = CloudServerInventoryStack(app, "UAT",
        stack_name = "CloudServerInventoryStack",
        description = "This stack will create lambda function and lambda role",
        build_table = False
        )

Tags.of(Stack1).add("Environment","Dev")
Tags.of(Stack2).add("Environment","UAT")

# Add a tag to all constructs in the stack
tags = {'Name': 'Ops-Server-Inventory-Stack', 
        'Service':'AWSSecurity', 
        'CreatedWith':'AWSCDK'}

for key, value in tags.items():
    Tags.of(app).add(key, value)

app.synth()
