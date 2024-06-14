#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (Tags)
from pipelines.pipelines_stack import PipelinesStack


app         = cdk.App()

ENV         = app.node.try_get_context("env")

stack       = PipelinesStack(app, "PipelinesStack", 
              stack_name    = "BuildingStackWithCDK",
              description   = "Stack will build CodeBuildProject and CodePipeline",
              existing_role = True)

# Add a tag to all constructs in the stack
tags        = {
            'Name': 'BuildingStackWithCDK', 
            'Git': app.node.try_get_context("GitOwner") + '/' + app.node.try_get_context("GitRepository")
            }

for key, value in tags.items():
    Tags.of(app).add(key, value)

if ENV == "dev":
  Tags.of(app).add("Environment","Dev")
if ENV == "prod":
  Tags.of(app).add("Environment", "Prod")
if ENV == "uat":
  Tags.of(app).add("Environment", "UAT")


app.synth()
