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
        
        # Lambda function for FastAPI
        api_lambda = _lambda.DockerImageFunction(
            self, "EventsApiFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../backend",
                file="Dockerfile"
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            environment={
                "DYNAMODB_TABLE_NAME": events_table.table_name,
                "CORS_ORIGINS": "*",  # Configure as needed
            }
        )
        
        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)
        
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
