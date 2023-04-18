from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as _lambda,
    Duration,
    Stack,
    Tags
)
from constructs import Construct

class FindIdleInstancesStack(Stack):
    """
    A stack that deploys a Lambda function and CloudWatch Events rule to track unused IAM policies.
    """

    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        # Permissions for lambda functions
        inline_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=['*'],
            actions=[
                'ec2:DescribeInstances',
                'cloudwatch:GetMetricStatistics',
                'sns:Publish'
            ])

        lambda_policy = iam.Policy(self, 'NewPolicy', policy_name="GetMetricsPolicy")
        lambda_policy.add_statements(inline_policy)

        lambda_role = iam.Role(
            self,
            "LambdaPermissions",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="LambdaRoleForGetServerMetrics",
            description="Lambda Role to Get EC2 Metrics"
        )

        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLambdaInsightsExecutionRolePolicy"))
        lambda_role.attach_inline_policy(lambda_policy)

        # Define variables
        sns_topic = self.node.try_get_context("sns_topic")
        account_id = self.node.try_get_context("account_id")

        # Create the Lambda layer
        my_layer = _lambda.LayerVersion(self, "MyLayer",
            code=_lambda.Code.from_asset("./lambda/layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        # Import an existing layer
        lambda_insights_layer = _lambda.LayerVersion.from_layer_version_arn(self, 'LambdaInsightsLayer',
            layer_version_arn='arn:aws:lambda:us-east-1:580247275435:layer:LambdaInsightsExtension:35')

        # Create the Lambda function with the included pytz package
        find_idle_instances_lambda = _lambda.Function(self, "FindIdleInstances",
                                                      runtime=_lambda.Runtime.PYTHON_3_9,
                                                      handler="lambda_handler.lambda_handler",
                                                      code=_lambda.Code.from_asset("./lambda/code"),
                                                      timeout=Duration.seconds(180),
                                                      memory_size=128,
                                                      role = lambda_role,
                                                      environment={
                                                          "SNS_TOPIC_ARN": sns_topic,
                                                          "MPLCONFIGDIR": "/tmp",
                                                          "AWS_ACCOUNT_ID": account_id
                                                      })
        
        # Add the layer to the function
        find_idle_instances_lambda.add_layers(lambda_insights_layer)
        find_idle_instances_lambda.add_layers(my_layer)

        # Run every day at 10.00PM UTC (05.00 Eastern Time)
        rule_start = events.Rule(
            self, "FindIdleInstances-Trigger-Rule",
            rule_name='FindIdleInstances-Trigger-Rule',
            schedule=events.Schedule.cron(
                minute='0',
                hour='10')
        )
        rule_start.add_target(targets.LambdaFunction(find_idle_instances_lambda))

        # Adding tag Name to resources, otherwise it will inherit stack Name tag
        Tags.of(find_idle_instances_lambda).add("Name", "FindIdleInstances")
        Tags.of(lambda_role).add("Name", "LambdaRoleForGetServerMetrics")
