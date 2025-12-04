# Design Document

## Overview

This design document outlines the refactoring of the backend codebase from a monolithic structure to a layered architecture with clear separation of concerns. The refactoring will extract business logic from API handlers into service modules, organize database operations into repository patterns, and structure the code into domain-based folders. The primary goal is to improve code maintainability, testability, and scalability while ensuring all existing functionality remains intact.

The refactoring follows a three-layer architecture:
1. **API Layer (Handlers/Controllers)**: Manages HTTP concerns (request/response, status codes, error formatting)
2. **Service Layer**: Contains business logic and orchestrates operations
3. **Repository Layer**: Encapsulates database access patterns

## Architecture

### Current Structure
```
backend/
├── main.py           # All API handlers with embedded business logic
├── models.py         # Pydantic models
├── database.py       # DynamoDB client with all database operations
└── test_api.py       # API tests
```

### Target Structure
```
backend/
├── main.py                      # FastAPI app initialization, middleware, Lambda handler
├── api/                         # API layer
│   ├── __init__.py
│   ├── events.py               # Event endpoints
│   ├── users.py                # User endpoints
│   └── registrations.py        # Registration endpoints
├── services/                    # Service layer (business logic)
│   ├── __init__.py
│   ├── event_service.py
│   ├── user_service.py
│   └── registration_service.py
├── repositories/                # Repository layer (data access)
│   ├── __init__.py
│   ├── event_repository.py
│   ├── user_repository.py
│   └── registration_repository.py
├── models/                      # Domain models
│   ├── __init__.py
│   ├── event.py
│   ├── user.py
│   └── registration.py
├── common/                      # Shared utilities
│   ├── __init__.py
│   ├── exceptions.py           # Custom exceptions
│   └── database.py             # Database client initialization
└── test_api.py                 # Existing API tests (should pass unchanged)
```

### Layer Responsibilities

**API Layer (api/)**
- Receive and validate HTTP requests using Pydantic models
- Call appropriate service methods
- Format responses and set HTTP status codes
- Handle HTTP-specific errors (404, 409, 422, 500)
- No business logic or database calls

**Service Layer (services/)**
- Implement business rules and validation
- Orchestrate operations across multiple repositories
- Handle domain-specific logic (e.g., waitlist promotion, capacity checks)
- Return domain objects or raise domain exceptions
- No HTTP concerns or direct database calls

**Repository Layer (repositories/)**
- Encapsulate all DynamoDB operations
- Provide CRUD methods and domain-specific queries
- Handle database errors and translate to domain exceptions
- Return domain objects or None
- No business logic

## Components and Interfaces

### Event Domain

**EventRepository**
```python
class EventRepository:
    def create(self, event_data: dict) -> dict
    def get_by_id(self, event_id: str) -> Optional[dict]
    def list_all(self, status_filter: Optional[str] = None) -> List[dict]
    def update(self, event_id: str, update_data: dict) -> Optional[dict]
    def delete(self, event_id: str) -> bool
```

**EventService**
```python
class EventService:
    def create_event(self, event_data: dict) -> dict
    def get_event(self, event_id: str) -> dict  # Raises NotFoundError
    def list_events(self, status_filter: Optional[str] = None) -> List[dict]
    def update_event(self, event_id: str, update_data: dict) -> dict  # Raises NotFoundError
    def delete_event(self, event_id: str) -> None  # Raises NotFoundError
```

**Event API Handlers** (in api/events.py)
- POST /events
- GET /events
- GET /events/{event_id}
- PUT /events/{event_id}
- DELETE /events/{event_id}

### User Domain

**UserRepository**
```python
class UserRepository:
    def create(self, user_data: dict) -> dict  # Raises on duplicate
    def get_by_id(self, user_id: str) -> Optional[dict]
```

**UserService**
```python
class UserService:
    def create_user(self, user_data: dict) -> dict  # Raises DuplicateError
    def get_user(self, user_id: str) -> dict  # Raises NotFoundError
```

**User API Handlers** (in api/users.py)
- POST /users
- GET /users/{userId}

### Registration Domain

**RegistrationRepository**
```python
class RegistrationRepository:
    def create(self, registration_data: dict) -> dict  # Raises on duplicate
    def get(self, user_id: str, event_id: str) -> Optional[dict]
    def delete(self, user_id: str, event_id: str) -> bool
    def list_by_user(self, user_id: str) -> List[dict]
    def list_by_event(self, event_id: str, status: Optional[str] = None) -> List[dict]
    def count_confirmed(self, event_id: str) -> int
    def get_first_waitlisted(self, event_id: str) -> Optional[dict]
    def update_status(self, user_id: str, event_id: str, status: str) -> dict
```

**RegistrationService**
```python
class RegistrationService:
    def register_user(self, user_id: str, event_id: str) -> dict
        # Business logic: check capacity, determine status, handle waitlist
    def unregister_user(self, user_id: str, event_id: str) -> None
        # Business logic: promote waitlisted user if applicable
    def list_user_registrations(self, user_id: str) -> List[dict]
        # Enriches with event details
    def list_event_registrations(self, event_id: str, status: Optional[str] = None) -> List[dict]
```

**Registration API Handlers** (in api/registrations.py)
- POST /registrations
- DELETE /registrations/{userId}/{eventId}
- GET /users/{userId}/registrations
- POST /events/{eventId}/registrations
- GET /events/{eventId}/registrations
- DELETE /events/{eventId}/registrations/{userId}

## Data Models

The existing Pydantic models in models.py will be split into domain-specific files:

**models/event.py**
- EventStatus (enum)
- EventBase
- EventCreate
- EventUpdate
- Event

**models/user.py**
- UserCreate
- User

**models/registration.py**
- RegistrationStatus (enum)
- RegistrationCreate
- EventRegistrationCreate
- Registration
- UserRegistration

All models maintain their current validation rules and field definitions.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing the acceptance criteria, most requirements are architectural and structural (code organization, dependency management, layer separation) which are not amenable to property-based testing. However, Requirement 4 contains critical functional properties that ensure the refactoring preserves existing behavior.

The testable properties focus on behavioral equivalence before and after refactoring:
- Property 1 validates that all endpoints continue to work with valid inputs
- Property 2 validates that error handling remains consistent with invalid inputs
- Property 3 validates that validation rules are preserved

These three properties provide comprehensive coverage of functional correctness during refactoring. Properties 1 and 3 could potentially be combined, but keeping them separate makes failures easier to diagnose (success vs validation).

### Property 1: Response equivalence for valid requests

*For any* valid API request (endpoint, method, and payload), the response structure, data, and status code should be identical before and after refactoring

**Validates: Requirements 4.2**

### Property 2: Error handling equivalence for invalid requests

*For any* invalid API request (malformed payload, missing required fields, invalid IDs), the error response structure, status code, and error message should be identical before and after refactoring

**Validates: Requirements 4.3**

### Property 3: Validation rule preservation

*For any* input that violates validation constraints (empty strings, out-of-range values, invalid formats), the validation error should be identical before and after refactoring

**Validates: Requirements 4.5**

## Error Handling

### Custom Exceptions (common/exceptions.py)

```python
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class NotFoundError(DomainException):
    """Raised when a resource is not found"""
    pass

class DuplicateError(DomainException):
    """Raised when attempting to create a duplicate resource"""
    pass

class CapacityError(DomainException):
    """Raised when event capacity is exceeded"""
    pass
```

### Exception Handling Flow

1. **Repository Layer**: Catches database errors, translates to domain exceptions
2. **Service Layer**: Catches repository exceptions, applies business logic, may raise domain exceptions
3. **API Layer**: Catches domain exceptions, translates to HTTP responses with appropriate status codes

**Exception to HTTP Status Code Mapping:**
- NotFoundError → 404
- DuplicateError → 409
- CapacityError → 409
- ValidationError (Pydantic) → 422
- DomainException → 500
- Unexpected exceptions → 500

## Testing Strategy

### Unit Testing

Unit tests will verify specific behaviors and integration points:

**Service Layer Tests:**
- Test business logic with mocked repositories
- Verify capacity checks and waitlist logic
- Test error conditions (not found, duplicates, capacity exceeded)
- Verify service methods call correct repository methods

**Repository Layer Tests:**
- Test CRUD operations with mocked DynamoDB client
- Verify query construction and filtering
- Test error handling and exception translation

**API Layer Tests:**
- Existing tests in test_api.py should pass without modification
- Tests verify end-to-end request/response flow
- Tests cover all endpoints, status codes, and error cases

### Property-Based Testing

Property-based testing will verify that the refactoring preserves existing behavior. We'll use **Hypothesis** for Python property-based testing with a minimum of 100 iterations per test.

**Test Configuration:**
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(...)
def test_property(...):
    ...
```

**Property Test Requirements:**
- Each property-based test MUST be tagged with a comment referencing the design document property
- Tag format: `# Feature: code-organization, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Tests should compare behavior before and after refactoring

**Test Approach:**

Since we're refactoring existing code, we'll use a snapshot/comparison approach:
1. Capture responses from current implementation for various inputs
2. After refactoring, generate the same inputs and compare responses
3. Alternatively, run both implementations side-by-side during transition

**Property Test Generators:**
- Generate valid event data (various titles, dates, capacities, statuses)
- Generate valid user data (various userIds, names)
- Generate valid registration scenarios (user/event combinations)
- Generate invalid inputs (empty strings, out-of-range values, malformed data)
- Generate edge cases (boundary values, special characters)

### Testing Library

**Property-Based Testing Framework:** Hypothesis (https://hypothesis.readthedocs.io/)
- Mature Python library for property-based testing
- Integrates with pytest
- Provides rich set of strategies for generating test data
- Supports stateful testing for complex scenarios

## Migration Strategy

The refactoring will be performed incrementally to minimize risk:

1. **Phase 1**: Create new folder structure and move models
2. **Phase 2**: Extract repositories from database.py
3. **Phase 3**: Create service layer with business logic
4. **Phase 4**: Refactor API handlers to use services
5. **Phase 5**: Update imports and remove old code
6. **Phase 6**: Verify all tests pass

Each phase should maintain a working state where existing tests pass.
