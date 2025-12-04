# Design Document: User Registration System

## Overview

The user registration system extends the existing events API to support user management and event registration with capacity constraints and waitlist functionality. The system will enable users to register for events, manage capacity limits, handle waitlists when events are full, and allow users to view their registrations.

The design follows the existing FastAPI architecture with DynamoDB as the data store, maintaining consistency with the current events API patterns. The system introduces three new data models (User, Registration, and enhanced Event) and corresponding API endpoints while preserving the existing event management functionality.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI App    │
│  (Lambda)       │
├─────────────────┤
│ • User Mgmt     │
│ • Registration  │
│ • Event Mgmt    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DynamoDB      │
├─────────────────┤
│ • Users Table   │
│ • Events Table  │
│ • Registrations │
│   Table         │
└─────────────────┘
```

### Component Interaction Flow

**Registration Flow:**
1. User submits registration request via API
2. FastAPI validates request and checks user/event existence
3. System queries event capacity and current registrations
4. System determines if user gets confirmed or waitlisted status
5. Registration record is created in DynamoDB
6. Response returned to user with registration status

**Unregistration Flow:**
1. User submits unregistration request via API
2. System retrieves registration record
3. If user was confirmed and waitlist exists, promote first waitlisted user
4. Registration record is deleted
5. If promotion occurred, update promoted user's registration
6. Response returned to user

### Data Storage Strategy

The system will use three DynamoDB tables:
- **Users Table**: Stores user information with userId as partition key
- **Events Table**: Extends existing table with capacity and waitlist fields
- **Registrations Table**: Uses composite key (userId + eventId) to track registrations

## Components and Interfaces

### 1. User Management Component

**Responsibilities:**
- Create and store user accounts
- Validate user data
- Retrieve user information

**API Endpoints:**
- `POST /users` - Create a new user
- `GET /users/{userId}` - Retrieve user information

**Pydantic Models:**
```python
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)

class User(BaseModel):
    userId: str
    name: str
```

### 2. Event Capacity Component

**Responsibilities:**
- Extend existing Event model with capacity and waitlist fields
- Validate capacity constraints
- Track available spots

**Enhanced Event Model:**
```python
class EventBase(BaseModel):
    # ... existing fields ...
    capacity: int = Field(..., gt=0, le=100000)
    hasWaitlist: bool = Field(default=False)
```

**Note:** The existing Event model already has a capacity field, so we only need to add the `hasWaitlist` boolean field.

### 3. Registration Management Component

**Responsibilities:**
- Handle registration requests
- Enforce capacity constraints
- Manage waitlist logic
- Process unregistrations
- Promote waitlisted users

**API Endpoints:**
- `POST /registrations` - Register user for event
- `DELETE /registrations/{userId}/{eventId}` - Unregister user from event
- `GET /users/{userId}/registrations` - List user's registrations

**Pydantic Models:**
```python
class RegistrationStatus(str, Enum):
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"

class RegistrationCreate(BaseModel):
    userId: str
    eventId: str

class Registration(BaseModel):
    userId: str
    eventId: str
    status: RegistrationStatus
    registeredAt: str  # ISO timestamp
    
class UserRegistration(BaseModel):
    eventId: str
    eventTitle: str
    status: RegistrationStatus
    registeredAt: str
```

### 4. Database Client Extensions

**New Methods:**
```python
class DynamoDBClient:
    # User operations
    def create_user(self, user_data: dict) -> dict
    def get_user(self, user_id: str) -> Optional[dict]
    
    # Registration operations
    def create_registration(self, registration_data: dict) -> dict
    def get_registration(self, user_id: str, event_id: str) -> Optional[dict]
    def delete_registration(self, user_id: str, event_id: str) -> bool
    def list_user_registrations(self, user_id: str) -> List[dict]
    def list_event_registrations(self, event_id: str, status: Optional[str] = None) -> List[dict]
    def count_confirmed_registrations(self, event_id: str) -> int
    def get_first_waitlisted_user(self, event_id: str) -> Optional[dict]
    def update_registration_status(self, user_id: str, event_id: str, status: str) -> dict
```

## Data Models

### DynamoDB Table Schemas

**Users Table:**
```
Table Name: users
Partition Key: userId (String)

Attributes:
- userId: String (PK)
- name: String
```

**Events Table (Enhanced):**
```
Table Name: events
Partition Key: eventId (String)

Attributes:
- eventId: String (PK)
- title: String
- description: String
- date: String
- location: String
- capacity: Number
- organizer: String
- status: String
- hasWaitlist: Boolean (NEW)
```

**Registrations Table:**
```
Table Name: registrations
Partition Key: userId (String)
Sort Key: eventId (String)

Attributes:
- userId: String (PK)
- eventId: String (SK)
- status: String (confirmed | waitlisted)
- registeredAt: String (ISO timestamp)

Global Secondary Index: EventRegistrationsIndex
- Partition Key: eventId
- Sort Key: registeredAt
- Purpose: Query all registrations for an event in order
```

### Registration Status State Machine

```
┌──────────────┐
│  No Record   │
└──────┬───────┘
       │ register()
       ▼
┌──────────────┐     capacity available
│  CONFIRMED   │◄────────────────────────┐
└──────┬───────┘                         │
       │                                 │
       │ unregister()          promote() │
       │                                 │
       ▼                                 │
┌──────────────┐                         │
│   Deleted    │                         │
└──────────────┘                         │
                                         │
┌──────────────┐     capacity full       │
│  WAITLISTED  │◄────────────────────────┘
└──────┬───────┘     + waitlist enabled
       │
       │ unregister()
       │
       ▼
┌──────────────┐
│   Deleted    │
└──────────────┘
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User creation round-trip
*For any* valid userId and name, creating a user and then retrieving it should return the same userId and name.
**Validates: Requirements 1.1, 1.4**

### Property 2: Invalid user names are rejected
*For any* string that is empty or contains only whitespace characters, attempting to create a user with that name should be rejected with an error.
**Validates: Requirements 1.2**

### Property 3: Duplicate userId rejection
*For any* existing user, attempting to create another user with the same userId should be rejected with an error.
**Validates: Requirements 1.3**

### Property 4: Event capacity configuration round-trip
*For any* valid capacity value and waitlist flag, creating or updating an event with those settings and then retrieving it should return the same capacity and waitlist values.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 5: Registration with available capacity
*For any* event with available capacity (confirmed registrations < capacity) and any valid user, registering that user should create a registration with confirmed status.
**Validates: Requirements 3.1**

### Property 6: Full event without waitlist rejection
*For any* event at capacity (confirmed registrations = capacity) with no waitlist enabled, attempting to register a new user should be rejected with an error.
**Validates: Requirements 3.2**

### Property 7: Full event with waitlist creates waitlisted registration
*For any* event at capacity (confirmed registrations = capacity) with waitlist enabled, registering a new user should create a registration with waitlisted status.
**Validates: Requirements 3.3**

### Property 8: Duplicate registration rejection
*For any* existing registration, attempting to register the same user for the same event again should be rejected with an error.
**Validates: Requirements 3.4**

### Property 9: Non-existent event registration rejection
*For any* non-existent eventId and valid userId, attempting to register should be rejected with an error.
**Validates: Requirements 3.5**

### Property 10: Non-existent user registration rejection
*For any* non-existent userId and valid eventId, attempting to register should be rejected with an error.
**Validates: Requirements 3.6**

### Property 11: Unregistration removes record
*For any* confirmed registration on an event without waitlisted users, unregistering should remove the registration record.
**Validates: Requirements 4.1**

### Property 12: Unregistration promotes waitlisted user
*For any* confirmed registration on an event with waitlisted users, unregistering should remove the registration record and promote the first waitlisted user (by registeredAt timestamp) to confirmed status.
**Validates: Requirements 4.2**

### Property 13: Waitlisted user unregistration
*For any* waitlisted registration, unregistering should remove the registration record without promoting any other users.
**Validates: Requirements 4.3**

### Property 14: Invalid unregistration rejection
*For any* user and event where no registration exists, attempting to unregister should be rejected with an error.
**Validates: Requirements 4.4**

### Property 15: Non-existent event unregistration rejection
*For any* non-existent eventId, attempting to unregister should be rejected with an error.
**Validates: Requirements 4.5**

### Property 16: User registrations list completeness
*For any* user with multiple registrations (both confirmed and waitlisted), requesting their registered events should return all registrations with correct status information for each.
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 17: Non-existent user registrations rejection
*For any* non-existent userId, requesting registered events should be rejected with an error.
**Validates: Requirements 5.5**

## Error Handling

### Error Categories

**Validation Errors (HTTP 422):**
- Empty or whitespace-only user names
- Invalid userId or eventId formats
- Missing required fields

**Not Found Errors (HTTP 404):**
- User does not exist
- Event does not exist
- Registration does not exist

**Conflict Errors (HTTP 409):**
- Duplicate userId
- Duplicate registration
- Event at capacity without waitlist

**Internal Server Errors (HTTP 500):**
- DynamoDB connection failures
- Unexpected database errors

### Error Response Format

All errors will follow the FastAPI standard error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Atomic Operations

Critical operations that must be atomic:
1. **Registration creation with capacity check**: Check capacity and create registration in a single transaction
2. **Unregistration with promotion**: Remove registration and promote waitlisted user atomically
3. **User creation with uniqueness check**: Verify userId doesn't exist and create user atomically

DynamoDB conditional expressions will be used to ensure atomicity:
- `attribute_not_exists(userId)` for user creation
- `attribute_not_exists(userId) AND attribute_not_exists(eventId)` for registration creation
- Transactional writes for unregistration with promotion

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

**User Management:**
- Create user with valid data
- Create user with empty name
- Create user with duplicate userId
- Retrieve existing user
- Retrieve non-existent user

**Event Capacity:**
- Create event with capacity and waitlist enabled
- Create event with capacity and waitlist disabled
- Update event capacity
- Update event waitlist flag

**Registration:**
- Register for event with available capacity
- Register for full event without waitlist
- Register for full event with waitlist
- Duplicate registration attempt
- Register with non-existent user
- Register with non-existent event

**Unregistration:**
- Unregister confirmed user without waitlist
- Unregister confirmed user with waitlist promotion
- Unregister waitlisted user
- Unregister non-existent registration

**List Registrations:**
- List registrations for user with multiple events
- List registrations for user with no events
- List registrations for non-existent user

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using the **Hypothesis** library for Python. Each property test will run a minimum of 100 iterations.

**Testing Framework:** Hypothesis (Python property-based testing library)

**Property Test Requirements:**
- Each property-based test MUST be tagged with a comment referencing the correctness property from this design document
- Tag format: `# Feature: user-registration, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Each test MUST run at least 100 iterations

**Property Test Coverage:**
- Property 1: User creation round-trip (generate random valid userIds and names)
- Property 2: Invalid user names rejection (generate whitespace-only strings)
- Property 3: Duplicate userId rejection (create user, attempt duplicate)
- Property 4: Event capacity configuration round-trip (generate random capacity and waitlist values)
- Property 5: Registration with available capacity (generate events with capacity, register users)
- Property 6: Full event without waitlist rejection (create full events, attempt registration)
- Property 7: Full event with waitlist (create full events with waitlist, verify waitlisted status)
- Property 8: Duplicate registration rejection (create registration, attempt duplicate)
- Property 9: Non-existent event registration rejection (generate random non-existent eventIds)
- Property 10: Non-existent user registration rejection (generate random non-existent userIds)
- Property 11: Unregistration removes record (create registration, unregister, verify removal)
- Property 12: Unregistration promotes waitlisted user (create confirmed + waitlisted, unregister, verify promotion)
- Property 13: Waitlisted user unregistration (create waitlisted registration, unregister, verify no promotion)
- Property 14: Invalid unregistration rejection (attempt unregister without registration)
- Property 15: Non-existent event unregistration rejection (generate random non-existent eventIds)
- Property 16: User registrations list completeness (create multiple registrations, verify all returned)
- Property 17: Non-existent user registrations rejection (generate random non-existent userIds)

**Test Data Generators:**
- Valid userIds: alphanumeric strings 1-100 characters
- Valid names: non-empty strings 1-200 characters
- Invalid names: empty strings and whitespace-only strings
- Valid eventIds: existing event identifiers
- Non-existent eventIds: random UUIDs not in database
- Capacity values: integers between 1 and 100000
- Waitlist flags: boolean values
- Registration timestamps: ISO format datetime strings

### Integration Testing

Integration tests will verify end-to-end workflows:
- Complete registration flow from user creation to event registration
- Waitlist promotion flow when confirmed users unregister
- Multiple users registering for the same event concurrently
- User viewing their registrations across multiple events

### Test Execution Strategy

1. **Implementation-first development**: Implement features before writing corresponding tests
2. **Unit tests**: Write unit tests for specific examples and edge cases
3. **Property tests**: Write property-based tests for universal properties
4. **Integration tests**: Write end-to-end workflow tests
5. **Validation**: Ensure all tests pass before considering feature complete
