from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_iam as iam,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets

)
from constructs import Construct

class GetCredentialReportsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Using existing role for lambda
        lambda_role = iam.Role.from_role_arn(self, "LambdaRole", self.node.try_get_context("lambda_role"),
            mutable=False
        )

        # Using existing SNS topic
        topic = self.node.try_get_context("topic")

        # Create lambda function
        with open("lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        lambdaFn = lambda_.Function(
            self, "GetCredentialReportLambdaFunction",
            function_name = "GetCredentialReport",
            code=lambda_.InlineCode(handler_code),
            handler="index.handler",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment= {
                        'sns_topic': (topic)
                        },
            role = (lambda_role)
            )

        # Run every Monday at 12PM UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "ScheduledEventRule",
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
 
