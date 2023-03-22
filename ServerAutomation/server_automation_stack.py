from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_events as events

)
from constructs import Construct

class ServerAutomationStack(Stack):
    """
    A stack that deploys a Lambda function and two scheduled CloudWatch Events to start and stop EC2 instances.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes the ServerAutomationStack class.

        Args:
            scope (Construct): The parent construct.
            construct_id (str): The name of the stack.
            **kwargs: Other keyword arguments that are passed to the Stack constructor.
        """
        super().__init__(scope, construct_id, **kwargs)

        # Permissions for lambda functions
        inline_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, 
            resources=['*'], 
            actions=[
            'ec2:Describe*', 
            'ec2:Report*',
            'ec2:Start*',
            'ec2:Stop*'
            ])
        
        instance_policy = iam.Policy(self, 'newpolicy', policy_name="ScheduleInstancePolicy")
        instance_policy.add_statements(inline_policy)
        
        lambda_role = iam.Role(self, "LambdaPermissions",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="RoleForScheduledInstancesFunction",
            description="Role For Scheduled Instances Function"
        )
        
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.attach_inline_policy(instance_policy)
        
        # Create lambda function
        lambdaFn = lambda_.Function(
            self, "ScheduleInstancesFunction",
            function_name = "ScheduleInstancesFunction",
            code = lambda_.Code.from_asset("lambda"),
            handler = "lambda_handler.handler",
            timeout = Duration.seconds(120),
            runtime = lambda_.Runtime.PYTHON_3_9,
            role = (lambda_role)
            )
      
        # Run every day at 10.00PM UTC (05.00 Eastern Time)
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule_start = events.Rule(
            self, "StartInstanceRule",
            rule_name='StartInstances',
            schedule=events.Schedule.cron(
                minute='0',
                hour='10')
        )
        rule_start.add_target(targets.LambdaFunction(lambdaFn))

        # Run every day at 01.00AM UTC (20.00 Eastern Time)
        rule_stop = events.Rule(
            self, "StopInstanceRule",
            rule_name='StopInstances',
            schedule=events.Schedule.cron(
                minute='0',
                hour='1')
        )
        rule_stop.add_target(targets.LambdaFunction(lambdaFn))

        # Adding tag Name to resources, otherwise it will inherit stack Name tag
        Tags.of(lambdaFn).add("Name", "Schedule-Instances-Function")
        Tags.of(lambda_role).add("Name", "RoleForScheduledInstancesFunction")
