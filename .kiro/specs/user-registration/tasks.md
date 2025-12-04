# Implementation Plan: User Registration System

- [ ] 1. Extend data models for user registration
- [ ] 1.1 Add User models to models.py
  - Create UserCreate and User Pydantic models with validation
  - Add field validators for userId and name
  - _Requirements: 1.1, 1.2_

- [ ] 1.2 Add Registration models to models.py
  - Create RegistrationStatus enum (confirmed, waitlisted)
  - Create RegistrationCreate, Registration, and UserRegistration models
  - Add timestamp field with ISO format
  - _Requirements: 3.1, 3.3, 5.3_

- [ ] 1.3 Enhance Event model with waitlist support
  - Add hasWaitlist boolean field to EventBase model
  - Update EventCreate and EventUpdate models
  - _Requirements: 2.2, 2.3_

- [ ]* 1.4 Write property test for user creation round-trip
  - **Property 1: User creation round-trip**
  - **Validates: Requirements 1.1, 1.4**

- [ ]* 1.5 Write property test for invalid user names
  - **Property 2: Invalid user names are rejected**
  - **Validates: Requirements 1.2**

- [ ]* 1.6 Write property test for event capacity configuration
  - **Property 4: Event capacity configuration round-trip**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [ ] 2. Extend database client for user and registration operations
- [ ] 2.1 Add user management methods to database.py
  - Implement create_user with conditional expression for uniqueness
  - Implement get_user method
  - Handle DynamoDB ClientError exceptions
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 2.2 Add registration query methods to database.py
  - Implement get_registration method
  - Implement list_user_registrations method
  - Implement list_event_registrations with status filter
  - Implement count_confirmed_registrations method
  - _Requirements: 3.1, 5.1, 5.2_

- [ ] 2.3 Add registration creation method to database.py
  - Implement create_registration with conditional expression to prevent duplicates
  - Include registeredAt timestamp generation
  - _Requirements: 3.1, 3.3, 3.4_

- [ ] 2.4 Add registration deletion and promotion methods to database.py
  - Implement delete_registration method
  - Implement get_first_waitlisted_user method (query by registeredAt)
  - Implement update_registration_status method
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 2.5 Write property test for duplicate userId rejection
  - **Property 3: Duplicate userId rejection**
  - **Validates: Requirements 1.3**

- [ ] 3. Implement user management API endpoints
- [ ] 3.1 Add POST /users endpoint to main.py
  - Validate user data with Pydantic
  - Call db_client.create_user
  - Handle duplicate userId errors (409 Conflict)
  - Handle validation errors (422)
  - Return created user (201)
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3.2 Add GET /users/{userId} endpoint to main.py
  - Call db_client.get_user
  - Handle user not found (404)
  - Return user data
  - _Requirements: 1.4_

- [ ]* 3.3 Write unit tests for user endpoints
  - Test create user with valid data
  - Test create user with empty name
  - Test create user with duplicate userId
  - Test get existing user
  - Test get non-existent user
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Implement registration API endpoints
- [ ] 4.1 Add POST /registrations endpoint to main.py
  - Validate registration data with Pydantic
  - Verify user exists (call get_user)
  - Verify event exists (call get_event)
  - Count confirmed registrations for event
  - Determine status (confirmed if capacity available, waitlisted if full with waitlist, error if full without waitlist)
  - Call db_client.create_registration
  - Handle duplicate registration errors (409 Conflict)
  - Handle non-existent user/event errors (404)
  - Handle full event without waitlist (409 Conflict)
  - Return created registration (201)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ]* 4.2 Write property test for registration with available capacity
  - **Property 5: Registration with available capacity**
  - **Validates: Requirements 3.1**

- [ ]* 4.3 Write property test for full event without waitlist
  - **Property 6: Full event without waitlist rejection**
  - **Validates: Requirements 3.2**

- [ ]* 4.4 Write property test for full event with waitlist
  - **Property 7: Full event with waitlist creates waitlisted registration**
  - **Validates: Requirements 3.3**

- [ ]* 4.5 Write property test for duplicate registration
  - **Property 8: Duplicate registration rejection**
  - **Validates: Requirements 3.4**

- [ ]* 4.6 Write property test for non-existent event registration
  - **Property 9: Non-existent event registration rejection**
  - **Validates: Requirements 3.5**

- [ ]* 4.7 Write property test for non-existent user registration
  - **Property 10: Non-existent user registration rejection**
  - **Validates: Requirements 3.6**

- [ ] 4.8 Add DELETE /registrations/{userId}/{eventId} endpoint to main.py
  - Verify registration exists (call get_registration)
  - Get registration status
  - Delete registration
  - If status was confirmed and event has waitlist, get first waitlisted user and promote to confirmed
  - Handle registration not found (404)
  - Handle non-existent event (404)
  - Return success message
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 4.9 Write property test for unregistration removes record
  - **Property 11: Unregistration removes record**
  - **Validates: Requirements 4.1**

- [ ]* 4.10 Write property test for waitlist promotion
  - **Property 12: Unregistration promotes waitlisted user**
  - **Validates: Requirements 4.2**

- [ ]* 4.11 Write property test for waitlisted user unregistration
  - **Property 13: Waitlisted user unregistration**
  - **Validates: Requirements 4.3**

- [ ]* 4.12 Write property test for invalid unregistration
  - **Property 14: Invalid unregistration rejection**
  - **Validates: Requirements 4.4**

- [ ]* 4.13 Write property test for non-existent event unregistration
  - **Property 15: Non-existent event unregistration rejection**
  - **Validates: Requirements 4.5**

- [ ] 4.14 Add GET /users/{userId}/registrations endpoint to main.py
  - Verify user exists (call get_user)
  - Call db_client.list_user_registrations
  - For each registration, fetch event details
  - Build UserRegistration response objects
  - Handle non-existent user (404)
  - Return list of registrations with event details
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 4.15 Write property test for user registrations list
  - **Property 16: User registrations list completeness**
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ]* 4.16 Write property test for non-existent user registrations
  - **Property 17: Non-existent user registrations rejection**
  - **Validates: Requirements 5.5**

- [ ]* 4.17 Write unit tests for registration endpoints
  - Test register for event with available capacity
  - Test register for full event without waitlist
  - Test register for full event with waitlist
  - Test duplicate registration
  - Test register with non-existent user
  - Test register with non-existent event
  - Test unregister confirmed user without waitlist
  - Test unregister confirmed user with waitlist promotion
  - Test unregister waitlisted user
  - Test unregister non-existent registration
  - Test list registrations for user with events
  - Test list registrations for user with no events
  - Test list registrations for non-existent user
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 5. Update infrastructure for new DynamoDB tables
- [ ] 5.1 Add Users table to backend_stack.py
  - Create DynamoDB table with userId as partition key
  - Configure on-demand billing
  - Grant Lambda function read/write permissions
  - _Requirements: 1.1_

- [ ] 5.2 Add Registrations table to backend_stack.py
  - Create DynamoDB table with userId as partition key and eventId as sort key
  - Add Global Secondary Index (EventRegistrationsIndex) with eventId as partition key and registeredAt as sort key
  - Configure on-demand billing
  - Grant Lambda function read/write permissions
  - _Requirements: 3.1, 4.2_

- [ ] 5.3 Update environment variables in backend_stack.py
  - Add USERS_TABLE_NAME environment variable to Lambda
  - Add REGISTRATIONS_TABLE_NAME environment variable to Lambda
  - _Requirements: 1.1, 3.1_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 7. Write integration tests for end-to-end workflows
- [ ]* 7.1 Write integration test for complete registration flow
  - Create user, create event, register user, verify registration
  - _Requirements: 1.1, 2.1, 3.1_

- [ ]* 7.2 Write integration test for waitlist promotion flow
  - Create users, create event at capacity with waitlist, register users, unregister confirmed user, verify promotion
  - _Requirements: 3.3, 4.2_

- [ ]* 7.3 Write integration test for user viewing registrations
  - Create user, create multiple events, register for events, list registrations, verify all present
  - _Requirements: 5.1, 5.2, 5.3_
