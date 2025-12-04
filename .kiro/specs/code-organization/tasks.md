# Implementation Plan

- [ ] 1. Create new folder structure and organize models
  - Create api/, services/, repositories/, models/, and common/ directories
  - Split models.py into domain-specific files (event.py, user.py, registration.py)
  - Create __init__.py files for proper Python package structure
  - Update imports in existing files to reference new model locations
  - _Requirements: 3.1, 3.2, 3.5_

- [ ] 2. Extract and organize database client
  - Create common/database.py with DynamoDB client initialization
  - Move database connection logic from database.py to common/database.py
  - Ensure database client can be imported by repositories
  - _Requirements: 3.4_

- [ ] 3. Create repository layer for events
  - Implement EventRepository in repositories/event_repository.py
  - Extract event-related database operations from database.py
  - Implement methods: create, get_by_id, list_all, update, delete
  - Handle database errors and return domain objects
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 4. Create repository layer for users
  - Implement UserRepository in repositories/user_repository.py
  - Extract user-related database operations from database.py
  - Implement methods: create, get_by_id
  - Handle duplicate user errors appropriately
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 5. Create repository layer for registrations
  - Implement RegistrationRepository in repositories/registration_repository.py
  - Extract registration-related database operations from database.py
  - Implement methods: create, get, delete, list_by_user, list_by_event, count_confirmed, get_first_waitlisted, update_status
  - Handle duplicate registration errors appropriately
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 6. Create custom exception classes
  - Implement exception hierarchy in common/exceptions.py
  - Define DomainException, NotFoundError, DuplicateError, CapacityError
  - Document exception usage and HTTP status code mappings
  - _Requirements: 5.3_

- [ ] 7. Create service layer for events
  - Implement EventService in services/event_service.py
  - Extract business logic from event API handlers in main.py
  - Implement methods: create_event, get_event, list_events, update_event, delete_event
  - Use EventRepository for data access
  - Raise appropriate domain exceptions (NotFoundError)
  - _Requirements: 1.1, 1.3, 1.5, 2.2, 5.2_

- [ ] 8. Create service layer for users
  - Implement UserService in services/user_service.py
  - Extract business logic from user API handlers in main.py
  - Implement methods: create_user, get_user
  - Use UserRepository for data access
  - Handle duplicate user errors and raise DuplicateError
  - _Requirements: 1.1, 1.3, 1.5, 2.2, 5.2_

- [ ] 9. Create service layer for registrations
  - Implement RegistrationService in services/registration_service.py
  - Extract complex business logic: capacity checks, waitlist management, user promotion
  - Implement methods: register_user, unregister_user, list_user_registrations, list_event_registrations
  - Use RegistrationRepository, EventRepository, and UserRepository
  - Handle capacity limits and raise CapacityError when appropriate
  - _Requirements: 1.1, 1.3, 1.5, 2.2, 5.2_

- [ ] 10. Refactor event API handlers
  - Create api/events.py with event endpoint handlers
  - Refactor handlers to use EventService instead of direct database calls
  - Ensure handlers only contain HTTP concerns (validation, response formatting, status codes)
  - Translate domain exceptions to HTTP responses
  - Maintain existing endpoint paths and response structures
  - _Requirements: 1.2, 1.4, 4.1, 4.2, 5.1_

- [ ] 11. Refactor user API handlers
  - Create api/users.py with user endpoint handlers
  - Refactor handlers to use UserService instead of direct database calls
  - Ensure handlers only contain HTTP concerns
  - Translate DuplicateError to 409 status code
  - Maintain existing endpoint paths and response structures
  - _Requirements: 1.2, 1.4, 4.1, 4.2, 5.1_

- [ ] 12. Refactor registration API handlers
  - Create api/registrations.py with registration endpoint handlers
  - Refactor handlers to use RegistrationService instead of direct database calls
  - Ensure handlers only contain HTTP concerns
  - Translate domain exceptions to appropriate HTTP status codes
  - Maintain existing endpoint paths and response structures
  - _Requirements: 1.2, 1.4, 4.1, 4.2, 5.1_

- [ ] 13. Update main.py to use new API modules
  - Import and register routes from api/events.py, api/users.py, api/registrations.py
  - Keep FastAPI app initialization, CORS middleware, and global exception handler
  - Keep Lambda handler (Mangum) in main.py
  - Remove old endpoint definitions
  - Ensure all endpoints are properly registered
  - _Requirements: 4.1_

- [ ] 14. Checkpoint - Ensure all existing tests pass
  - Run existing test suite (test_api.py) without modifications
  - Verify all endpoints return expected responses
  - Verify error handling works correctly
  - Ask the user if questions arise
  - _Requirements: 4.4_

- [ ]* 15. Write property-based test for response equivalence
  - **Property 1: Response equivalence for valid requests**
  - **Validates: Requirements 4.2**
  - Use Hypothesis to generate valid event, user, and registration data
  - Compare responses from refactored implementation against expected behavior
  - Configure test to run 100 iterations minimum
  - Tag test with: `# Feature: code-organization, Property 1: Response equivalence for valid requests`

- [ ]* 16. Write property-based test for error handling equivalence
  - **Property 2: Error handling equivalence for invalid requests**
  - **Validates: Requirements 4.3**
  - Use Hypothesis to generate invalid inputs (missing fields, invalid IDs, malformed data)
  - Verify error responses match expected status codes and error structures
  - Configure test to run 100 iterations minimum
  - Tag test with: `# Feature: code-organization, Property 2: Error handling equivalence for invalid requests`

- [ ]* 17. Write property-based test for validation preservation
  - **Property 3: Validation rule preservation**
  - **Validates: Requirements 4.5**
  - Use Hypothesis to generate inputs that violate validation constraints
  - Verify validation errors are identical to expected behavior
  - Configure test to run 100 iterations minimum
  - Tag test with: `# Feature: code-organization, Property 3: Validation rule preservation`

- [ ] 18. Clean up old code
  - Remove old database.py file (replaced by repositories)
  - Remove any unused imports
  - Verify no circular dependencies exist
  - Update any documentation or comments
  - _Requirements: 3.3, 5.4_

- [ ] 19. Final checkpoint - Verify complete system
  - Run all tests including property-based tests
  - Verify all endpoints work correctly
  - Check that code organization matches design
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
