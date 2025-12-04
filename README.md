# Events API - Serverless Application

A fully serverless REST API for managing events with user registration, capacity management, and waitlist functionality. Built with FastAPI, AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **Backend**: FastAPI application running on AWS Lambda (ARM64)
- **API Gateway**: Public HTTPS endpoint with CORS support
- **Database**: DynamoDB for serverless data storage (3 tables: Events, Users, Registrations)
- **Infrastructure**: AWS CDK for Infrastructure as Code
- **Container**: Docker-based Lambda deployment

## Features

### Event Management
- ✅ Full CRUD operations for events
- ✅ Custom event IDs support
- ✅ Status-based filtering
- ✅ Event capacity limits
- ✅ Waitlist functionality

### User Management
- ✅ User account creation and retrieval
- ✅ User validation (unique IDs, non-empty names)

### Registration System
- ✅ User registration for events
- ✅ Automatic capacity management
- ✅ Waitlist when events are full
- ✅ Automatic waitlist promotion on cancellations
- ✅ View user registrations with event details
- ✅ View event registrations with status

### Technical Features
- ✅ Input validation with Pydantic
- ✅ CORS enabled for web access
- ✅ Comprehensive error handling
- ✅ Unit and integration tests
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

## Data Models

### Event Properties

- `eventId` (string) - Unique identifier (auto-generated or custom)
- `title` (string) - Event title (1-200 characters)
- `description` (string) - Event description (1-1000 characters)
- `date` (string) - Event date (ISO format or YYYY-MM-DD)
- `location` (string) - Event location (1-200 characters)
- `capacity` (integer) - Maximum attendees (1-100,000)
- `organizer` (string) - Event organizer (1-100 characters)
- `status` (enum) - Event status: active, scheduled, ongoing, completed, cancelled
- `hasWaitlist` (boolean) - Whether waitlist is enabled (also accepts `waitlistEnabled`)

### User Properties

- `userId` (string) - Unique user identifier (1-100 characters)
- `name` (string) - User name (1-200 characters, cannot be empty or whitespace-only)

### Registration Properties

- `userId` (string) - User identifier
- `eventId` (string) - Event identifier
- `status` (enum) - Registration status: confirmed, waitlisted
- `registeredAt` (string) - ISO timestamp of registration

## API Endpoints

**Base URL**: `https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/`

### Event Endpoints

- `GET /events` - List all events
- `GET /events?status=active` - Filter events by status
- `POST /events` - Create a new event
- `GET /events/{eventId}` - Get a specific event
- `PUT /events/{eventId}` - Update an event
- `DELETE /events/{eventId}` - Delete an event

### User Endpoints

- `POST /users` - Create a new user
- `GET /users/{userId}` - Get a specific user
- `GET /users/{userId}/registrations` - List all registrations for a user

### Registration Endpoints (Standard)

- `POST /registrations` - Register a user for an event
- `DELETE /registrations/{userId}/{eventId}` - Unregister a user from an event

### Registration Endpoints (Event-based)

- `POST /events/{eventId}/registrations` - Register a user for an event
- `GET /events/{eventId}/registrations` - List all registrations for an event
- `DELETE /events/{eventId}/registrations/{userId}` - Unregister a user from an event

### System Endpoints

- `GET /health` - Health check
- `GET /` - API information

### Example Usage

#### Event Management

**Create an event with waitlist:**
```bash
curl -X POST https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "tech-conf-2024",
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 100,
    "organizer": "Tech Corp",
    "status": "active",
    "hasWaitlist": true
  }'
```

**List all events:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events
```

**Get a specific event:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024
```

#### User Management

**Create a user:**
```bash
curl -X POST https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "name": "John Doe"
  }'
```

**Get a user:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/users/user-123
```

#### Registration Management

**Register a user for an event (standard endpoint):**
```bash
curl -X POST https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/registrations \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "eventId": "tech-conf-2024"
  }'
```

**Register a user for an event (event-based endpoint):**
```bash
curl -X POST https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/registrations \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123"
  }'
```

**List all registrations for an event:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/registrations
```

**List all registrations for a user:**
```bash
curl https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/users/user-123/registrations
```

**Unregister a user from an event:**
```bash
curl -X DELETE https://fk20uw7pjj.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/registrations/user-123
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

## Registration System Behavior

### Capacity Management

When a user registers for an event:
1. **Available capacity**: User gets `confirmed` status
2. **Event full + waitlist enabled**: User gets `waitlisted` status
3. **Event full + no waitlist**: Registration is rejected with 409 error

### Automatic Waitlist Promotion

When a confirmed user unregisters from an event with a waitlist:
1. The registration is deleted
2. The first waitlisted user (by registration timestamp) is automatically promoted to `confirmed` status
3. This happens atomically to prevent race conditions

### Example Flow

```bash
# Event has capacity of 2 with waitlist enabled
# User 1 registers -> confirmed (1/2)
# User 2 registers -> confirmed (2/2 - FULL)
# User 3 registers -> waitlisted (event full)
# User 1 unregisters -> User 3 automatically promoted to confirmed
```

## Testing

The project includes comprehensive unit and integration tests:

```bash
cd backend
pytest -v
```

Tests cover:
- All CRUD operations for events, users, and registrations
- Custom eventId support
- Status filtering
- Capacity management
- Waitlist functionality
- Automatic promotion logic
- Input validation
- Error handling (404, 409, 422, 500)
- End-to-end registration workflows

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
