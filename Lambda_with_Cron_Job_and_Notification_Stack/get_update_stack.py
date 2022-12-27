from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_sns as sns,
    aws_chatbot as chatbot,
    aws_sns_subscriptions as sub,
    aws_iam as iam,
    aws_kms as kms,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets

)
from constructs import Construct

class GetUpdateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Using existing role for chatbot
        role = iam.Role.from_role_arn(self, "Role", self.node.try_get_context("existing_role"),
            mutable=False
        )

        # Using existing role for lambda
        lambda_role = iam.Role.from_role_arn(self, "LambdaRole", self.node.try_get_context("lambda_role"),
            mutable=False
        )

        # Using existing KMS key
        key = kms.Key.from_key_arn(self, "key", self.node.try_get_context("sns_key"))

        # existing topic for lambda function
        ex_topic = self.node.try_get_context("existing_sns")

        # Create SNS topic
        topic = sns.Topic(
            self, "TOPIC-NAME",
            display_name="TOPIC-NAME",
            topic_name="TOPIC-NAME",
            master_key=(key)
        )
    

        topic.add_subscription(sub.UrlSubscription("https://global.sns-api.chatbot.amazonaws.com"))

        # Create chatbot configuration
        target = chatbot.SlackChannelConfiguration(self, "CHATBOT-NAME",
            slack_channel_configuration_name="CHATBOT-NAME",
            slack_workspace_id="SLACK-WORKSPACE-ID",
            slack_channel_id="SLACK-CHANNEL-ID",
            logging_level=chatbot.LoggingLevel('ERROR'),
            role=(role)
        )
     
        target.add_notification_topic(topic)

        # Create lambda function
        with open("lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        lambdaFn = lambda_.Function(
            self, "Singleton",
            code=lambda_.InlineCode(handler_code),
            handler="index.main",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment= {
                        'sns_topic': (ex_topic)
                        },
            role = (lambda_role)
            )

        # Run every Monday at 12PM UTC
        rule = events.Rule(
            self, "Rule",
            rule_name='RULE-NAME',
            schedule=events.Schedule.cron(
                minute='0',
                hour='12',
                month='*',
                week_day='MON',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        # Adding tag Name to resources, otherwise it will inherit slack Name tag
        Tags.of(topic).add("Name", "NAME")
        Tags.of(target).add("Name", "NAME")
        Tags.of(lambdaFn).add("Name", "NAME")
