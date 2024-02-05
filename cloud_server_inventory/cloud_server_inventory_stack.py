from aws_cdk import (
    CfnCondition,
    Fn,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as _lambda,
    Duration,
    Stack,
    Tags
)
from constructs import Construct
import os

class CloudServerInventoryStack(Stack):
    def __init__(self, scope: Construct, stack_id: str, build_table = False, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        # Create DynamoDB in Dev account 
        if build_table:
            table = dynamodb.Table(self, "ServerInventory",
                partition_key = dynamodb.Attribute(name = "InstanceId", type = dynamodb.AttributeType.STRING),
                sort_key = dynamodb.Attribute(name = "Account", type = dynamodb.AttributeType.STRING),
                table_name = "server-inventory-table"
            )
            Tags.of(table).add("Name", "server-inventory")
        else:
            table = None

        # Condition to build other resources, like IAM permissions. We don't need to build DynamoDB and Assumed Role in other accounts
        build_table_condition = CfnCondition(self, "BuildTableCondition",
        expression = Fn.condition_equals(build_table, True)
        )

        # List of all AWS accounts to assume the role, this would be helpfull if we don't have too much accounts
        # accounts_to_allow = [self.node.try_get_context("account_1"), self.node.try_get_context("account_2")]

        # Create a role that grants access to a DynamoDB table. This role will be assumed by lambda role in all accounts
        if build_table: 
            role_a = iam.Role(self, "RoleAssumed",
                assumed_by = iam.OrganizationPrincipal(self.node.try_get_context("org_id")),
                # assumed_by = iam.CompositePrincipal(
                #     # Use the map function to create a list of AccountPrincipal objects
                #     *map(iam.AccountPrincipal, accounts_to_allow)
                # ),
                description = "Role that allows cross-account access to the DynamoDB table"
            )
            Tags.of(role_a).add("Name", "CrossAccountRoleForDynamoDBUpdate")
        else:
            pass

        # Create a policy that grants access to a DynamoDB table
        if table:
            policy = iam.CfnPolicy(self, "Policy",
                policy_name = "DynamoDBPolicy",
                policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem"],
                            "Resource": table.table_arn
                        }
                    ]
                },
                roles = [role_a.role_name]
            )
            policy.cfn_options.condition = build_table_condition
            policy.add_depends_on(table.node.default_child)
            policy.add_depends_on(role_a.node.default_child)

            assume_policy_local = iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            resources = [role_a.role_arn],
            actions=[
                'sts:AssumeRole'
            ])

        # Permissions for lambda functions, needs to be created in all accounts
        inline_policy = iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            resources = ['*'],
            actions = [
                'ec2:DescribeInstances'
            ])
        
        assume_policy_other = iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            resources = [self.node.try_get_context("assumed_role")],
            actions=[
                'sts:AssumeRole'
            ])

        lambda_policy = iam.Policy(self, 'NewPolicy', policy_name = "GetServersPolicy")
        lambda_policy.add_statements(inline_policy)

        # Needs to be separated by condition
        if build_table:
            lambda_policy.add_statements(assume_policy_local)
        else:
            lambda_policy.add_statements(assume_policy_other)

        lambda_role = iam.Role(self, "LambdaPermissions",
            assumed_by = iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name = "LambdaRoleToGetInstances",
            description = "Lambda Role to Get EC2 Instances"
        )
        Tags.of(lambda_role).add("Name", "LambdaRoleForGetInstancesData")

        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.attach_inline_policy(lambda_policy)

        # Create the Lambda function, which will get the instance data and put in a DynamoDb table
        instances_lambda = _lambda.Function(self, "GetInstancesData",
                            runtime = _lambda.Runtime.PYTHON_3_9,
                            handler = "handler.handler",
                            code = _lambda.Code.from_asset("code"),
                            timeout = Duration.seconds(60),
                            memory_size = 128,
                            role = lambda_role
                            )
        instances_lambda.add_environment('account_id', os.environ["CDK_DEFAULT_ACCOUNT"])
        if build_table:
            instances_lambda.add_environment('assumed_role', role_a.role_arn)
            instances_lambda.add_environment('tablename', table.table_name)
        else:
            instances_lambda.add_environment('assumed_role', self.node.try_get_context("assumed_role"))
            instances_lambda.add_environment('tablename', self.node.try_get_context("tablename"))
        Tags.of(instances_lambda).add("Name", "GetInstancesData")

        # Run if there is 'RunInstances' or 'TerminateInstances' events
        rule_start = events.Rule(
            self, "FindInstances-Trigger-Rule",
            rule_name='FindInstances-Trigger-Rule',
            event_pattern = events.EventPattern(
                detail_type = ["AWS API Call via CloudTrail"],
                source = ["aws.ec2"],
                detail = {
                    "eventSource": ["ec2.amazonaws.com"],
                    "eventName": ["RunInstances", "TerminateInstances"]
                }
            )
        )
        rule_start.add_target(targets.LambdaFunction(instances_lambda))
        
