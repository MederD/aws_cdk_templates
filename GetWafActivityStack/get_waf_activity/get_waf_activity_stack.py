from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_sns as sns,
    aws_sns_subscriptions as sub,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_iam as iam

)
from constructs import Construct

class GetWafActivityStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment variables
        slack_url = self.node.try_get_context("slack_url")

        # Using existing role for lambda
        lambda_role = iam.Role.from_role_arn(self, "LambdaRole", self.node.try_get_context("lambda_role")
        )
        logGroupName = self.node.try_get_context("logGroupName")
        query = self.node.try_get_context("query")
        secretname = self.node.try_get_context("secretname")
        existinglayer = self.node.try_get_context("existinglayer")

        # Permissions for lambda functions
        secrets_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, 
            resources=['SECRET-ARN'], 
            actions=[
            'secretsmanager:GetSecretValue'
            ])
        

        access_secrets_policy = iam.Policy(self, 'access_secrets_policy', policy_name="access_secrets_policy")
        access_secrets_policy.add_statements(secrets_policy)
        lambda_role.attach_inline_policy(access_secrets_policy)
      
        # Consumer lambda function
        lambdaSNS = lambda_.Function(
            self, "SNSConsumerFunction",
            function_name = "SNSToSlackFunction-WAFActivity",
            code=lambda_.Code.from_asset("lambda/sns_function"),
            handler="index.handler",
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
            display_name="SlackNotificationTopic-WAFActivity",
            topic_name="SlackNotificationTopic-WAFActivity"
        )

        topic.add_subscription(sub.LambdaSubscription(lambdaSNS))

        layer = lambda_.LayerVersion.from_layer_version_arn(self, "ExistingLayer", existinglayer)

        # Producer lambda function
        lambdaFn = lambda_.Function(
            self, "GetWAFActivityFunction",
            function_name = "GetWAFActivityFunction",
            code=lambda_.Code.from_asset("lambda/code"),
            handler="index.handler",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment= {
                        'sns_topic': (topic.topic_arn),
                        'logGroupName': logGroupName,
                        'query': query,
                        'secretname': secretname
                        },
            role = (lambda_role),
            layers = [layer]
            )
     

        # Run every 10 minutes
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            rule_name='Get-WAFActivity-Scheduled-Rule',
            schedule=events.Schedule.expression("cron(0/10 * * * ? *)")
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        # Adding tag Name to resources, otherwise it will inherit stack Name tag
        Tags.of(lambdaFn).add("Name", "Get-WAFActivity-Function")
        Tags.of(lambdaSNS).add("Name", "SNS-To-Slack-WAFActivity-Function")
        Tags.of(topic).add("Name", "Slack-Notification-WAFActivity-Topic")
 
