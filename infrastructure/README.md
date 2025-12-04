# CDK Infrastructure

Serverless infrastructure for the Events API using AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **AWS Lambda** - Runs FastAPI application using Docker container
- **API Gateway** - Provides public HTTPS endpoint with CORS support
- **DynamoDB** - Serverless NoSQL database for event storage
- **Mangum** - ASGI adapter to run FastAPI on Lambda

## Prerequisites

- AWS CLI configured with credentials
- Docker installed and running
- Python 3.11+
- AWS CDK CLI: `npm install -g aws-cdk`

## Setup

```bash
pip install -r requirements.txt
```

## Bootstrap CDK (first time only)

```bash
cdk bootstrap
```

## Deploy

```bash
cdk deploy
```

This will:
1. Build the Docker image for the Lambda function
2. Create the DynamoDB table
3. Deploy the Lambda function
4. Set up API Gateway with CORS
5. Output the public API URL

## Useful Commands

* `cdk ls` - List all stacks
* `cdk synth` - Synthesize CloudFormation template
* `cdk deploy` - Deploy stack to AWS
* `cdk diff` - Compare deployed stack with current state
* `cdk destroy` - Remove stack from AWS

## After Deployment

The API URL will be displayed in the outputs. You can test it:

```bash
curl https://your-api-id.execute-api.region.amazonaws.com/prod/health
```

## Cost Optimization

- Lambda: Pay per request (free tier: 1M requests/month)
- DynamoDB: On-demand pricing (pay per request)
- API Gateway: Pay per request (free tier: 1M requests/month)

This setup is cost-effective for low to medium traffic applications.
