from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_sns as sns,
    aws_chatbot as chatbot,
    aws_sns_subscriptions as sub,
    aws_iam as iam,
    aws_kms as kms
)
from constructs import Construct

class CdkSnsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Using existing role
        role = iam.Role.from_role_arn(self, "Role", self.node.try_get_context("existing_role"),
            mutable=False
        )

        # Using existing KMS key
        key = kms.Key.from_key_arn(self, "key", self.node.try_get_context("sns_key"))

        # Create SNS topic
        topic = sns.Topic(
            self, "YOUR-SNS-TOPIC-NAME",
            display_name="YOUR-SNS-TOPIC-NAME",
            topic_name="YOUR-SNS-TOPIC-NAME",
            master_key=(key)
        )
    

        topic.add_subscription(sub.UrlSubscription("https://global.sns-api.chatbot.amazonaws.com"))

        # Create chatbot configuration
        target = chatbot.SlackChannelConfiguration(self, "YOUR-CHATBOT-CONFIGURATION-NAME",
            slack_channel_configuration_name="YOUR-CHATBOT-CONFIGURATION-NAME",
            slack_workspace_id="YOUR-SLACK-WORKSPACE-ID",
            slack_channel_id="YOUR-SLACK-CHANNEL-ID",
            logging_level=chatbot.LoggingLevel('ERROR'),
            role=(role)
        )
     
        target.add_notification_topic(topic)

        # Adding tag Name to resources, otherwise it will inherit slack Name tag
        Tags.of(topic).add("Name", "YOUR-SNS-TOPIC-NAME")
        Tags.of(target).add("Name", "YOUR-CHATBOT-CONFIGURATION-NAME")

