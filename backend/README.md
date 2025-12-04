# Events API - FastAPI Backend

REST API for managing events with DynamoDB storage.

## Features

- Full CRUD operations for events
- DynamoDB integration
- Input validation with Pydantic
- CORS support
- Error handling
- OpenAPI documentation

## Event Properties

- `eventId` (string, auto-generated)
- `title` (string, 1-200 chars)
- `description` (string, 1-1000 chars)
- `date` (ISO format string)
- `location` (string, 1-200 chars)
- `capacity` (integer, 1-100000)
- `organizer` (string, 1-100 chars)
- `status` (enum: scheduled, ongoing, completed, cancelled)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AWS configuration
```

## Run

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API docs at http://localhost:8000/docs

## API Endpoints

- `POST /events` - Create a new event
- `GET /events` - List all events
- `GET /events/{event_id}` - Get a specific event
- `PUT /events/{event_id}` - Update an event
- `DELETE /events/{event_id}` - Delete an event
- `GET /health` - Health check

## Environment Variables

- `DYNAMODB_TABLE_NAME` - DynamoDB table name (default: events)
- `AWS_REGION` - AWS region (default: us-west-2)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `DYNAMODB_ENDPOINT_URL` - Optional local DynamoDB endpoint

## Testing

Run unit tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

The tests validate:
- All CRUD operations
- Custom eventId support
- Status filtering
- Input validation
- Error handling (404, 422, 500)
