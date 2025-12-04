# CDK Infrastructure

Serverless infrastructure for the Events API with user registration system using AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **AWS Lambda** - Runs FastAPI application using Docker container (ARM64)
- **API Gateway** - Provides public HTTPS endpoint with CORS support
- **DynamoDB** - Three tables for serverless data storage:
  - **Events Table** - Event information with capacity and waitlist settings
  - **Users Table** - User accounts
  - **Registrations Table** - User-event registrations with GSI for event queries
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
2. Create three DynamoDB tables:
   - Events table (partition key: eventId)
   - Users table (partition key: userId)
   - Registrations table (composite key: userId + eventId, with GSI on eventId)
3. Deploy the Lambda function with appropriate IAM permissions
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

## DynamoDB Tables

### Events Table
- **Partition Key**: eventId
- **Attributes**: title, description, date, location, capacity, organizer, status, hasWaitlist

### Users Table
- **Partition Key**: userId
- **Attributes**: name

### Registrations Table
- **Partition Key**: userId
- **Sort Key**: eventId
- **Attributes**: status, registeredAt
- **Global Secondary Index**: EventRegistrationsIndex
  - Partition Key: eventId
  - Sort Key: registeredAt
  - Purpose: Query all registrations for an event, ordered by registration time

## Cost Optimization

- Lambda: Pay per request (free tier: 1M requests/month)
- DynamoDB: On-demand pricing (pay per request, 25GB free storage)
- API Gateway: Pay per request (free tier: 1M requests/month)

This setup is cost-effective for low to medium traffic applications and stays within AWS free tier limits for typical usage.
