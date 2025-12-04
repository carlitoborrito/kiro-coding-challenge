---
inclusion: fileMatch
fileMatchPattern: '(main\.py|test_api\.py|.*api.*|.*endpoint.*)'
---

# API Standards

This document defines REST API conventions for the Events API project.

## HTTP Methods

- **GET**: Retrieve resources (list or single item)
- **POST**: Create new resources
- **PUT**: Update existing resources (full or partial updates)
- **DELETE**: Remove resources

## Status Codes

### Success Codes

- **200 OK**: Successful GET, PUT, DELETE operations
- **201 Created**: Successful POST operations (resource created)
- **204 No Content**: Successful DELETE with no response body (not used in this project)

### Client Error Codes

- **400 Bad Request**: Malformed request syntax
- **404 Not Found**: Resource does not exist
- **422 Unprocessable Entity**: Validation errors (Pydantic validation failures)

### Server Error Codes

- **500 Internal Server Error**: Unexpected server errors

## Error Response Format

All error responses follow FastAPI's standard format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422), FastAPI returns:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Validation error message",
      "type": "error_type"
    }
  ]
}
```

## Success Response Formats

### Single Resource

```json
{
  "eventId": "string",
  "title": "string",
  "description": "string",
  "date": "string",
  "location": "string",
  "capacity": 0,
  "organizer": "string",
  "status": "active"
}
```

### List of Resources

```json
[
  {
    "eventId": "string",
    "title": "string",
    ...
  },
  {
    "eventId": "string",
    "title": "string",
    ...
  }
]
```

### Delete Operation

```json
{
  "message": "Event deleted successfully"
}
```

## Endpoint Conventions

### Naming

- Use plural nouns for collections: `/events`
- Use resource ID in path for single items: `/events/{event_id}`
- Use query parameters for filtering: `/events?status=active`

### Request/Response

- **Content-Type**: `application/json`
- **Accept**: `application/json`
- All request bodies must be valid JSON
- All response bodies are JSON (except health checks)

## Validation Rules

- Use Pydantic models for all request/response validation
- Define field constraints in models (min_length, max_length, gt, le)
- Use custom validators for complex validation (e.g., date formats)
- Return 422 for validation failures with detailed error messages

## Error Handling

- Check resource existence before update/delete operations
- Return 404 with descriptive message when resource not found
- Catch all unexpected exceptions and return 500 with generic message
- Never expose internal error details or stack traces in production

## CORS Configuration

- Allow all origins in development (`*`)
- Configure specific origins for production
- Allow all standard HTTP methods
- Allow all headers for flexibility

## Query Parameters

- Use lowercase parameter names
- Use singular form: `status` not `statuses`
- Support optional filtering without breaking default behavior
- Document all query parameters in endpoint docstrings
