from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_s3 as s3,
    Stack,
    Tags
)
from constructs import Construct

class PipelinesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, existing_role = True, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment variables
        env                               = self.node.try_get_context("env")
        GitRepository                     = self.node.try_get_context("GitRepository")
        GitOwner                          = self.node.try_get_context("GitOwner")

        artifact_store_bucket             = self.node.try_get_context(f"{env}.ArtifactStoreBucket")
        CodeStarConnectionArn             = self.node.try_get_context(f"{env}.CodeStarConnectionArn")
        GitBranch                         = self.node.try_get_context(f"{env}.GitBranch")
        BuildspecFile                     = self.node.try_get_context(f"{env}.BuildspecFile")
        bucket_param                      = self.node.try_get_context(f"{env}.BucketParam")
 
        # Define the IAM role
        if existing_role:
            existing_build_role           = iam.Role.from_role_arn(self, "BuildRole", self.node.try_get_context(f"{env}.ExistingBuildRole"))
            existing_pipeline_role        = iam.Role.from_role_arn(self, "PipelineRole", self.node.try_get_context(f"{env}.ExistingPipelineRole"))
        else:
            existing_build_role           = iam.Role(self, "CodeBuildRole",
                assumed_by                = iam.ServicePrincipal('codebuild.amazonaws.com'),
                managed_policies          = [
                    iam.ManagedPolicy.from_aws_managed_policy_name('AWSCloudFormationFullAccess')
                    ]
            )
            existing_pipeline_role        = iam.Role(self, "CodePipelineRole",
                assumed_by                = iam.ServicePrincipal('codepipeline.amazonaws.com'),
                managed_policies          = [
                    iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodePipelineFullAccess')
                    ]
            )

            Tags.of(existing_build_role).add("Name", f"{self.stack_name}-CodeBuildRole")
            Tags.of(existing_pipeline_role).add("Name", f"{self.stack_name}-CodePipelineRole")

        # CodeBuild project configuration
        project                           = codebuild.PipelineProject(self, f"{self.stack_name}-BuildProject",
            environment                   = codebuild.BuildEnvironment(
                build_image               = codebuild.LinuxBuildImage.from_code_build_image_id('aws/codebuild/standard:6.0'),
                compute_type              = codebuild.ComputeType.SMALL
            ),
            build_spec                    = codebuild.BuildSpec.from_source_filename(BuildspecFile),
            role                          = existing_build_role,
            environment_variables         = {
                "BUILDSTAGE": codebuild.BuildEnvironmentVariable(
                    value                 = "#{variables.BUILDSTAGE}", 
                    type                  = codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                "BucketName": codebuild.BuildEnvironmentVariable(
                    value                 = "#{variables.BucketName}", 
                    type                  = codebuild.BuildEnvironmentVariableType.PLAINTEXT)
            }
        )

        # CodePipeline configuration
        source_output                     = codepipeline.Artifact()

        source_action                     = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name                   = "Remote_Source",
            owner                         = GitOwner,
            repo                          = GitRepository,
            branch                        = GitBranch,
            output                        = source_output,
            connection_arn                = CodeStarConnectionArn,
            variables_namespace           = "SourceVariables"
        )
        
        build_action                      = codepipeline_actions.CodeBuildAction(
            action_name                   = "CodeBuild",
            project                       = project,
            input                         = source_output,
            outputs                       = [codepipeline.Artifact()], 
            environment_variables         = {
                "BUILDSTAGE": codebuild.BuildEnvironmentVariable(
                    value                 = env,
                    type                  = codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                "BucketName": codebuild.BuildEnvironmentVariable(
                    value                 = bucket_param,
                    type                  = codebuild.BuildEnvironmentVariableType.PLAINTEXT)
            }
        )

        pipeline                          = codepipeline.Pipeline(self, f"{self.stack_name}-Pipeline",
            stages                        = [
                codepipeline.StageProps(
                stage_name                = "Source",
                actions                   = [source_action]
            ), codepipeline.StageProps(
                stage_name                = "Build",
                actions                   = [build_action]
            )
            ],
            artifact_bucket               = s3.Bucket.from_bucket_name(self, "ArtifactBucket", artifact_store_bucket),
            role                          = existing_pipeline_role,
            
        )

        # Adding tag Name to resources, otherwise it will inherit stack "Name" tag
        Tags.of(project).add("Name", f"{self.stack_name}-BuildProject")
        Tags.of(pipeline).add("Name", f"{self.stack_name}-Pipeline")
