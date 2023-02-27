import os
from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_sns as sns,
    aws_sns_subscriptions as sub,
    aws_iam as iam,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets

)
from constructs import Construct

class GetCredentialReportStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment variables
        slack_url = self.node.try_get_context("slack_url")

        # Permissions for lambda functions
        inline_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, 
            resources=['*'], 
            actions=[
            'iam:GenerateCredentialReport', 
            'iam:GetCredentialReport'
            ])
        
        lambda_role = iam.Role(self, "LambdaPermissions",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="LambdaRoleForCredentialReport",
            description="Lambda Role For Credential Report and Slack interaction"
        )

        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEventBridgeFullAccess"))
        lambda_role.add_to_policy(inline_policy)

        # Consumer lambda function
        lambdaSNS = lambda_.Function(
            self, "SNSConsumerFunction",
            function_name = "SNSToSlackFunction",
            code=lambda_.Code.from_asset("lambda"),
            handler="sns_lambda.handler",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment= {
                        'slack_url': (slack_url)
                        },
            role = (lambda_role)
            )

        # Create SNS topic
        topic = sns.Topic(
            self, "SNS-Topic",
            display_name="SlackNotificationTopic",
            topic_name="SlackNotificationTopic"
        )

        topic.add_subscription(sub.LambdaSubscription(lambdaSNS))

        # Producer lambda function
        lambdaFn = lambda_.Function(
            self, "GetCredentialReportFunction",
            function_name = "GetCredentialReport",
            code=lambda_.Code.from_asset("lambda"),
            handler="lambda_handler.handler",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment= {
                        'sns_topic': (topic.topic_arn),
                        'environment': os.environ["CDK_DEFAULT_ACCOUNT"]
                        },
            role = (lambda_role)
            )

        # Run every Monday at 12PM UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            rule_name='Get-Credential-Report-Scheduled-Rule',
            schedule=events.Schedule.cron(
                minute='0',
                hour='12',
                month='*',
                week_day='MON',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        # Adding tag Name to resources, otherwise it will inherit stack Name tag
        Tags.of(lambdaFn).add("Name", "Get-Credentials-Report-Function")
        Tags.of(lambdaSNS).add("Name", "SNS-To-Slack-Function")
        Tags.of(topic).add("Name", "Slack-Notification-Topic")
 
