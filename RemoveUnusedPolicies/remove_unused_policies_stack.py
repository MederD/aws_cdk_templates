from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    Duration,
    Stack,
    Tags
)
from constructs import Construct
import os


class RemoveUnusedPoliciesStack(Stack):
    """
    A stack that deploys a Lambda function and CloudWatch Events rule to track unused IAM policies.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes the RemoveUnusedPoliciesStack class.

        Args:
            scope (Construct): The parent construct.
            construct_id (str): The name of the stack.
            **kwargs: Other keyword arguments that are passed to the Stack constructor.
        """
        super().__init__(scope, construct_id, **kwargs)

        # Permissions for lambda functions
        inline_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "iam:GetPolicy",
                "iam:DeletePolicy",
                "iam:ListPolicies",
                "iam:ListPolicyVersions",
                "iam:DeletePolicyVersion",
                "sns:Publish"
            ]
        )

        lambda_role = iam.Role(
            self,
            "LambdaPermissions",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="LambdaRoleForRemoveUnusedPolicies",
            description="Lambda Role to Remove Unused IAM Policies"
        )

        instance_policy = iam.Policy(
            self,
            "DeletePolicies",
            policy_name="DeletePolicies"
        )
        instance_policy.add_statements(inline_policy)
        lambda_role.attach_inline_policy(instance_policy)
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        #Define variables
        sns_topic = self.node.try_get_context("sns_topic")

        # Create lambda function
        lambda_fn = lambda_.Function(
            self,
            "RemoveUnusedPoliciesFunction",
            function_name="RemoveUnusedPoliciesFunction",
            code=lambda_.Code.from_asset("lambda"),
            handler="lambda_handler.lambda_handler",
            timeout=Duration.seconds(60),
            runtime=lambda_.Runtime.PYTHON_3_9,
            role=lambda_role,
            environment= {
                        "sns_topic": (sns_topic),
                        "AccountId": os.environ["CDK_DEFAULT_ACCOUNT"]
                        },
        )

        # Create eventbridge rule pattern
        rule_pattern = events.EventPattern(
            source=["aws.iam"],
            detail_type=["AWS API Call via CloudTrail"],
            detail={
                "eventSource": ["iam.amazonaws.com"],
                "eventName": ["CreatePolicy"],
            }
        )

        # Create eventbridge rule
        iam_policy_rule = events.Rule(
            self,
            "iam_policy_rule",
            description="Trigger when an IAM policy is created",
            event_pattern=rule_pattern,
        )

        # Attach taget to eventbridge rule
        iam_policy_rule.add_target(targets.LambdaFunction(lambda_fn))

        # Adding tag Name to resources, otherwise it will inherit stack Name tag
        Tags.of(lambda_fn).add("Name", "RemoveUnusedPoliciesFunction")
        Tags.of(lambda_role).add("Name", "LambdaRoleForRemoveUnusedPolicies")
