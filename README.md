# Events API - Serverless Application

A fully serverless REST API for managing events, built with FastAPI, AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **Backend**: FastAPI application running on AWS Lambda (ARM64)
- **API Gateway**: Public HTTPS endpoint with CORS support
- **Database**: DynamoDB for serverless data storage
- **Infrastructure**: AWS CDK for Infrastructure as Code
- **Container**: Docker-based Lambda deployment

## Features

- ✅ Full CRUD operations for events
- ✅ Custom event IDs support
- ✅ Status-based filtering
- ✅ Input validation with Pydantic
- ✅ CORS enabled for web access
- ✅ Comprehensive error handling
- ✅ Unit tests with 100% endpoint coverage
- ✅ Serverless architecture (pay-per-use)

## Project Structure

```
.
├── backend/                 # FastAPI application
│   ├── main.py             # API endpoints and Lambda handler
│   ├── models.py           # Pydantic models for validation
│   ├── database.py         # DynamoDB client
│   ├── test_api.py         # Unit tests
│   ├── Dockerfile          # Lambda container image
│   └── requirements.txt    # Python dependencies
├── infrastructure/          # AWS CDK infrastructure
│   ├── app.py              # CDK app entry point
│   ├── stacks/             # CDK stack definitions
│   └── requirements.txt    # CDK dependencies
└── README.md               # This file
```

## Event Properties

Each event has the following properties:

- `eventId` (string) - Unique identifier (auto-generated or custom)
- `title` (string) - Event title (1-200 characters)
- `description` (string) - Event description (1-1000 characters)
- `date` (string) - Event date (ISO format or YYYY-MM-DD)
- `location` (string) - Event location (1-200 characters)
- `capacity` (integer) - Maximum attendees (1-100,000)
- `organizer` (string) - Event organizer (1-100 characters)
- `status` (enum) - Event status: active, scheduled, ongoing, completed, cancelled

## API Endpoints

**Base URL**: `https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/`

### Endpoints

- `GET /events` - List all events
- `GET /events?status=active` - Filter events by status
- `POST /events` - Create a new event
- `GET /events/{event_id}` - Get a specific event
- `PUT /events/{event_id}` - Update an event
- `DELETE /events/{event_id}` - Delete an event
- `GET /health` - Health check

### Example Usage

**Create an event:**
```bash
curl -X POST https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "my-event-123",
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "active"
  }'
```

**List all events:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events
```

**Get a specific event:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/my-event-123
```

**Update an event:**
```bash
curl -X PUT https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/my-event-123 \
  -H "Content-Type: application/json" \
  -d '{"capacity": 600}'
```

**Delete an event:**
```bash
curl -X DELETE https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/my-event-123
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker Desktop
- AWS CLI configured
- Node.js (for AWS CDK CLI)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Run Tests

```bash
cd backend
pytest -v
```

### Run Locally

```bash
cd backend
uvicorn main:app --reload
```

API will be available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

## Deployment

### Prerequisites

1. AWS CLI configured with credentials
2. Docker running
3. AWS CDK CLI installed: `npm install -g aws-cdk`

### Deploy to AWS

```bash
# Install infrastructure dependencies
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy
cdk deploy
```

The deployment will output the API URL.

### Update Deployment

```bash
cd infrastructure
cdk deploy
```

### Destroy Infrastructure

```bash
cd infrastructure
cdk destroy
```

## Cost Optimization

This serverless architecture is cost-effective:

- **Lambda**: Pay per request (1M free requests/month)
- **DynamoDB**: On-demand pricing (25GB free storage)
- **API Gateway**: Pay per request (1M free requests/month)

For low to medium traffic, this stays within AWS free tier limits.

## Testing

The project includes comprehensive unit tests:

```bash
cd backend
pytest -v
```

Tests cover:
- All CRUD operations
- Custom eventId support
- Status filtering
- Input validation
- Error handling (404, 422, 500)

## Documentation

- API Documentation: `backend/docs/index.html` (generated with pdoc)
- Interactive API Docs: `{API_URL}/docs` (FastAPI Swagger UI)
- OpenAPI Schema: `{API_URL}/openapi.json`

## Security

- CORS configured for web access
- Input validation on all endpoints
- IAM roles with least privilege
- DynamoDB encryption at rest (default)
- HTTPS only via API Gateway

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/{function-name} --follow
```

## Contributing

1. Run tests before committing
2. Follow existing code style
3. Update documentation for API changes

## License

MIT
