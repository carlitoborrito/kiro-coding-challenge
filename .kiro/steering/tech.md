# Technology Stack

## Backend

- **Framework**: FastAPI 0.115.0
- **Runtime**: Python 3.11+
- **Server**: Uvicorn (local), Mangum (Lambda adapter)
- **Validation**: Pydantic 2.9.0
- **Database Client**: boto3 1.35.0
- **Testing**: pytest 8.3.0, httpx 0.27.0

## Infrastructure

- **IaC**: AWS CDK (Python)
- **Compute**: AWS Lambda (ARM64 architecture)
- **API**: API Gateway REST API
- **Database**: DynamoDB (on-demand billing)
- **Deployment**: Docker container images

## Common Commands

### Backend Development

```bash
# Setup
cd backend
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=. --cov-report=html
```

### Infrastructure Deployment

```bash
# Setup
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy to AWS
cdk deploy

# View changes before deploy
cdk diff

# Synthesize CloudFormation template
cdk synth

# Destroy infrastructure
cdk destroy
```

### Docker

```bash
# Build backend image
cd backend
docker build -t events-api .
```

## Environment Variables

Backend uses `.env` file (see `.env.example`):
- `DYNAMODB_TABLE_NAME` - DynamoDB table name
- `AWS_REGION` - AWS region (default: us-west-2)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `DYNAMODB_ENDPOINT_URL` - Optional local DynamoDB endpoint
