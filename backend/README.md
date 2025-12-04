# Events API - FastAPI Backend

REST API for managing events with user registration, capacity management, and waitlist functionality. Uses DynamoDB for storage.

## Features

### Event Management
- Full CRUD operations for events
- Event capacity limits
- Waitlist functionality
- Status-based filtering

### User Management
- User account creation and retrieval
- User validation (unique IDs, non-empty names)

### Registration System
- User registration for events
- Automatic capacity management
- Waitlist when events are full
- Automatic waitlist promotion on cancellations
- View user registrations with event details
- View event registrations with status

### Technical Features
- DynamoDB integration (3 tables: Events, Users, Registrations)
- Input validation with Pydantic
- CORS support
- Comprehensive error handling
- OpenAPI documentation
- Unit and integration tests

## Data Models

### Event Properties

- `eventId` (string, auto-generated or custom)
- `title` (string, 1-200 chars)
- `description` (string, 1-1000 chars)
- `date` (ISO format string or YYYY-MM-DD)
- `location` (string, 1-200 chars)
- `capacity` (integer, 1-100000)
- `organizer` (string, 1-100 chars)
- `status` (enum: active, scheduled, ongoing, completed, cancelled)
- `hasWaitlist` (boolean, default: false) - also accepts `waitlistEnabled`

### User Properties

- `userId` (string, 1-100 chars, unique)
- `name` (string, 1-200 chars, cannot be empty or whitespace-only)

### Registration Properties

- `userId` (string)
- `eventId` (string)
- `status` (enum: confirmed, waitlisted)
- `registeredAt` (ISO timestamp)

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

### Event Endpoints
- `POST /events` - Create a new event
- `GET /events` - List all events (optional: ?status=active)
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

## Environment Variables

- `DYNAMODB_TABLE_NAME` - DynamoDB events table name
- `USERS_TABLE_NAME` - DynamoDB users table name
- `REGISTRATIONS_TABLE_NAME` - DynamoDB registrations table name
- `AWS_REGION` - AWS region (default: us-west-2)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `DYNAMODB_ENDPOINT_URL` - Optional local DynamoDB endpoint

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
- All CRUD operations for events, users, and registrations
- Custom eventId support
- Status filtering
- Capacity management
- Waitlist functionality
- Automatic promotion logic
- Input validation
- Error handling (404, 409, 422, 500)
- End-to-end registration workflows
