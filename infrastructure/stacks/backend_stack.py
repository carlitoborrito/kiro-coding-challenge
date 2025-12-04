from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table for events
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
        )
        
        # DynamoDB table for users
        users_table = dynamodb.Table(
            self, "UsersTable",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
        )
        
        # DynamoDB table for registrations
        registrations_table = dynamodb.Table(
            self, "RegistrationsTable",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
        )
        
        # Add Global Secondary Index for querying registrations by event
        registrations_table.add_global_secondary_index(
            index_name="EventRegistrationsIndex",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="registeredAt",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # Lambda function for FastAPI
        api_lambda = _lambda.DockerImageFunction(
            self, "EventsApiFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../backend",
                file="Dockerfile"
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            architecture=_lambda.Architecture.ARM_64,  # Match Docker image architecture
            environment={
                "DYNAMODB_TABLE_NAME": events_table.table_name,
                "USERS_TABLE_NAME": users_table.table_name,
                "REGISTRATIONS_TABLE_NAME": registrations_table.table_name,
                "CORS_ORIGINS": "*",  # Configure as needed
            }
        )
        
        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)
        users_table.grant_read_write_data(api_lambda)
        registrations_table.grant_read_write_data(api_lambda)
        
        # API Gateway REST API
        api = apigw.LambdaRestApi(
            self, "EventsApi",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"],
            ),
        )
        
        # Outputs
        CfnOutput(self, "ApiUrl", value=api.url, description="Events API URL")
        CfnOutput(self, "TableName", value=events_table.table_name, description="DynamoDB Table Name")
