# Project Structure

## Directory Layout

```
.
├── backend/                 # FastAPI application
│   ├── main.py             # API endpoints and Lambda handler
│   ├── models.py           # Pydantic models for validation
│   ├── database.py         # DynamoDB client
│   ├── test_api.py         # Unit tests
│   ├── Dockerfile          # Lambda container image
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── docs/               # Generated API documentation (pdoc)
├── infrastructure/          # AWS CDK infrastructure
│   ├── app.py              # CDK app entry point
│   ├── stacks/             # CDK stack definitions
│   │   └── backend_stack.py
│   ├── requirements.txt    # CDK dependencies
│   └── cdk.out/            # Generated CloudFormation (gitignored)
└── README.md               # Main documentation
```

## Code Organization

### Backend Module Structure

- **main.py**: FastAPI app, endpoints, CORS middleware, exception handlers, Lambda handler (Mangum)
- **models.py**: Pydantic models (EventBase, EventCreate, EventUpdate, Event) and EventStatus enum
- **database.py**: DynamoDB client wrapper with CRUD operations
- **test_api.py**: pytest tests covering all endpoints and error cases

### Infrastructure Module Structure

- **app.py**: CDK app initialization
- **stacks/backend_stack.py**: Defines Lambda function, API Gateway, DynamoDB table, IAM permissions

## Key Patterns

- **Separation of concerns**: API logic, data models, and database operations are in separate modules
- **Environment-based configuration**: Uses `.env` for local development, environment variables in Lambda
- **Infrastructure as code**: All AWS resources defined in CDK
- **Container-based deployment**: Lambda uses Docker images for consistent environments
- **ARM64 architecture**: Lambda functions use ARM64 for cost optimization

## Testing

Tests are located in `backend/test_api.py` and cover:
- All CRUD operations
- Custom eventId support
- Status filtering
- Input validation
- Error handling (404, 422, 500)
