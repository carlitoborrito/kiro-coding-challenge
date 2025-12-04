import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    """Mock the database client"""
    with patch('main.db_client') as mock:
        yield mock


def test_get_events_success(mock_db):
    """Test GET /events returns 200"""
    mock_db.list_events.return_value = [
        {
            "eventId": "test-event-1",
            "title": "Test Event",
            "description": "Test Description",
            "date": "2024-12-15",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Organizer",
            "status": "active"
        }
    ]
    
    response = client.get("/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_events_with_status_filter(mock_db):
    """Test GET /events?status=active returns 200"""
    mock_db.list_events.return_value = [
        {
            "eventId": "test-event-1",
            "title": "Active Event",
            "description": "Test Description",
            "date": "2024-12-15",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Organizer",
            "status": "active"
        }
    ]
    
    response = client.get("/events?status=active")
    assert response.status_code == 200
    mock_db.list_events.assert_called_once_with(status_filter="active")


def test_create_event_with_custom_id(mock_db):
    """Test POST /events with custom eventId returns 201"""
    event_data = {
        "date": "2024-12-15",
        "eventId": "api-test-event-456",
        "organizer": "API Test Organizer",
        "description": "Testing API Gateway integration",
        "location": "API Test Location",
        "title": "API Gateway Test Event",
        "capacity": 200,
        "status": "active"
    }
    
    mock_db.create_event.return_value = event_data
    
    response = client.post("/events", json=event_data)
    assert response.status_code == 201
    assert "eventId" in response.json()
    assert response.json()["eventId"] == "api-test-event-456"


def test_create_event_auto_generated_id(mock_db):
    """Test POST /events without eventId generates one"""
    event_data = {
        "date": "2024-12-15",
        "organizer": "Test Organizer",
        "description": "Test Description",
        "location": "Test Location",
        "title": "Test Event",
        "capacity": 100,
        "status": "active"
    }
    
    created_event = {**event_data, "eventId": "auto-generated-id"}
    mock_db.create_event.return_value = created_event
    
    response = client.post("/events", json=event_data)
    assert response.status_code == 201
    assert "eventId" in response.json()


def test_get_event_by_id_success(mock_db):
    """Test GET /events/{event_id} returns 200"""
    mock_db.get_event.return_value = {
        "eventId": "api-test-event-456",
        "title": "API Gateway Test Event",
        "description": "Testing API Gateway integration",
        "date": "2024-12-15",
        "location": "API Test Location",
        "capacity": 200,
        "organizer": "API Test Organizer",
        "status": "active"
    }
    
    response = client.get("/events/api-test-event-456")
    assert response.status_code == 200
    assert response.json()["eventId"] == "api-test-event-456"


def test_get_event_not_found(mock_db):
    """Test GET /events/{event_id} returns 404 when not found"""
    mock_db.get_event.return_value = None
    
    response = client.get("/events/nonexistent-id")
    assert response.status_code == 404


def test_update_event_success(mock_db):
    """Test PUT /events/{event_id} returns 200"""
    mock_db.get_event.return_value = {
        "eventId": "api-test-event-456",
        "title": "API Gateway Test Event",
        "description": "Testing API Gateway integration",
        "date": "2024-12-15",
        "location": "API Test Location",
        "capacity": 200,
        "organizer": "API Test Organizer",
        "status": "active"
    }
    
    mock_db.update_event.return_value = {
        "eventId": "api-test-event-456",
        "title": "Updated API Gateway Test Event",
        "description": "Testing API Gateway integration",
        "date": "2024-12-15",
        "location": "API Test Location",
        "capacity": 250,
        "organizer": "API Test Organizer",
        "status": "active"
    }
    
    update_data = {
        "title": "Updated API Gateway Test Event",
        "capacity": 250
    }
    
    response = client.put("/events/api-test-event-456", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated API Gateway Test Event"
    assert response.json()["capacity"] == 250


def test_update_event_not_found(mock_db):
    """Test PUT /events/{event_id} returns 404 when not found"""
    mock_db.get_event.return_value = None
    
    response = client.put("/events/nonexistent-id", json={"title": "Updated"})
    assert response.status_code == 404


def test_delete_event_success(mock_db):
    """Test DELETE /events/{event_id} returns 200"""
    mock_db.get_event.return_value = {
        "eventId": "api-test-event-456",
        "title": "Test Event",
        "description": "Test",
        "date": "2024-12-15",
        "location": "Test",
        "capacity": 100,
        "organizer": "Test",
        "status": "active"
    }
    mock_db.delete_event.return_value = True
    
    response = client.delete("/events/api-test-event-456")
    assert response.status_code == 200
    assert "message" in response.json()


def test_delete_event_not_found(mock_db):
    """Test DELETE /events/{event_id} returns 404 when not found"""
    mock_db.get_event.return_value = None
    
    response = client.delete("/events/nonexistent-id")
    assert response.status_code == 404


def test_health_check():
    """Test GET /health returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test GET / returns 200"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_event_validation_error():
    """Test POST /events with invalid data returns 422"""
    invalid_data = {
        "title": "",  # Empty title should fail validation
        "description": "Test",
        "date": "2024-12-15",
        "location": "Test",
        "capacity": 100,
        "organizer": "Test",
        "status": "active"
    }
    
    response = client.post("/events", json=invalid_data)
    assert response.status_code == 422


def test_create_event_invalid_capacity():
    """Test POST /events with invalid capacity returns 422"""
    invalid_data = {
        "title": "Test Event",
        "description": "Test",
        "date": "2024-12-15",
        "location": "Test",
        "capacity": 0,  # Must be > 0
        "organizer": "Test",
        "status": "active"
    }
    
    response = client.post("/events", json=invalid_data)
    assert response.status_code == 422


def test_create_event_invalid_date():
    """Test POST /events with invalid date format returns 422"""
    invalid_data = {
        "title": "Test Event",
        "description": "Test",
        "date": "invalid-date",
        "location": "Test",
        "capacity": 100,
        "organizer": "Test",
        "status": "active"
    }
    
    response = client.post("/events", json=invalid_data)
    assert response.status_code == 422


# User Management Tests

def test_create_user_with_valid_data(mock_db):
    """Test POST /users with valid data returns 201"""
    user_data = {
        "userId": "user123",
        "name": "John Doe"
    }
    
    mock_db.create_user.return_value = user_data
    
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["userId"] == "user123"
    assert response.json()["name"] == "John Doe"
    mock_db.create_user.assert_called_once()


def test_create_user_with_empty_name(mock_db):
    """Test POST /users with empty name returns 422"""
    user_data = {
        "userId": "user123",
        "name": ""
    }
    
    response = client.post("/users", json=user_data)
    assert response.status_code == 422


def test_create_user_with_whitespace_only_name(mock_db):
    """Test POST /users with whitespace-only name returns 422"""
    user_data = {
        "userId": "user123",
        "name": "   "
    }
    
    response = client.post("/users", json=user_data)
    assert response.status_code == 422


def test_create_user_with_duplicate_userId(mock_db):
    """Test POST /users with duplicate userId returns 409"""
    user_data = {
        "userId": "user123",
        "name": "John Doe"
    }
    
    # Simulate duplicate userId error from database
    mock_db.create_user.side_effect = ValueError("User with userId user123 already exists")
    
    response = client.post("/users", json=user_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_get_existing_user(mock_db):
    """Test GET /users/{userId} returns 200 for existing user"""
    mock_db.get_user.return_value = {
        "userId": "user123",
        "name": "John Doe"
    }
    
    response = client.get("/users/user123")
    assert response.status_code == 200
    assert response.json()["userId"] == "user123"
    assert response.json()["name"] == "John Doe"
    mock_db.get_user.assert_called_once_with("user123")


def test_get_non_existent_user(mock_db):
    """Test GET /users/{userId} returns 404 for non-existent user"""
    mock_db.get_user.return_value = None
    
    response = client.get("/users/nonexistent-user")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# Integration Tests for End-to-End Workflows

def test_complete_registration_flow(mock_db):
    """
    Integration test for complete registration flow
    Requirements: 1.1, 2.1, 3.1
    """
    # Step 1: Create a user
    user_data = {
        "userId": "integration-user-1",
        "name": "Integration Test User"
    }
    mock_db.create_user.return_value = user_data
    
    user_response = client.post("/users", json=user_data)
    assert user_response.status_code == 201
    assert user_response.json()["userId"] == "integration-user-1"
    
    # Step 2: Create an event with capacity
    event_data = {
        "eventId": "integration-event-1",
        "title": "Integration Test Event",
        "description": "Event for integration testing",
        "date": "2024-12-20",
        "location": "Test Location",
        "capacity": 50,
        "organizer": "Test Organizer",
        "status": "active",
        "hasWaitlist": False
    }
    mock_db.create_event.return_value = event_data
    
    event_response = client.post("/events", json=event_data)
    assert event_response.status_code == 201
    assert event_response.json()["eventId"] == "integration-event-1"
    assert event_response.json()["capacity"] == 50
    
    # Step 3: Register user for the event
    registration_data = {
        "userId": "integration-user-1",
        "eventId": "integration-event-1"
    }
    
    # Mock the verification and registration creation
    mock_db.get_user.return_value = user_data
    mock_db.get_event.return_value = event_data
    mock_db.count_confirmed_registrations.return_value = 0  # Event has capacity
    mock_db.create_registration.return_value = {
        "userId": "integration-user-1",
        "eventId": "integration-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }
    
    registration_response = client.post("/registrations", json=registration_data)
    assert registration_response.status_code == 201
    assert registration_response.json()["userId"] == "integration-user-1"
    assert registration_response.json()["eventId"] == "integration-event-1"
    assert registration_response.json()["status"] == "confirmed"
    
    # Step 4: Verify registration was created
    mock_db.get_registration.return_value = {
        "userId": "integration-user-1",
        "eventId": "integration-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }
    
    # Verify through list_user_registrations
    mock_db.list_user_registrations.return_value = [{
        "userId": "integration-user-1",
        "eventId": "integration-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }]
    
    list_response = client.get("/users/integration-user-1/registrations")
    assert list_response.status_code == 200
    registrations = list_response.json()
    assert len(registrations) == 1
    assert registrations[0]["eventId"] == "integration-event-1"
    assert registrations[0]["status"] == "confirmed"


def test_waitlist_promotion_flow(mock_db):
    """
    Integration test for waitlist promotion flow
    Requirements: 3.3, 4.2
    """
    # Step 1: Create multiple users
    user1_data = {"userId": "waitlist-user-1", "name": "User One"}
    user2_data = {"userId": "waitlist-user-2", "name": "User Two"}
    user3_data = {"userId": "waitlist-user-3", "name": "User Three"}
    
    # Step 2: Create an event at capacity with waitlist enabled
    event_data = {
        "eventId": "waitlist-event-1",
        "title": "Waitlist Test Event",
        "description": "Event for waitlist testing",
        "date": "2024-12-25",
        "location": "Test Location",
        "capacity": 2,  # Small capacity to test waitlist
        "organizer": "Test Organizer",
        "status": "active",
        "hasWaitlist": True
    }
    mock_db.create_event.return_value = event_data
    
    event_response = client.post("/events", json=event_data)
    assert event_response.status_code == 201
    assert event_response.json()["hasWaitlist"] is True
    
    # Step 3: Register first user (should be confirmed)
    mock_db.get_user.return_value = user1_data
    mock_db.get_event.return_value = event_data
    mock_db.count_confirmed_registrations.return_value = 0
    mock_db.create_registration.return_value = {
        "userId": "waitlist-user-1",
        "eventId": "waitlist-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }
    
    reg1_response = client.post("/registrations", json={
        "userId": "waitlist-user-1",
        "eventId": "waitlist-event-1"
    })
    assert reg1_response.status_code == 201
    assert reg1_response.json()["status"] == "confirmed"
    
    # Step 4: Register second user (should be confirmed)
    mock_db.get_user.return_value = user2_data
    mock_db.count_confirmed_registrations.return_value = 1
    mock_db.create_registration.return_value = {
        "userId": "waitlist-user-2",
        "eventId": "waitlist-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:05:00Z"
    }
    
    reg2_response = client.post("/registrations", json={
        "userId": "waitlist-user-2",
        "eventId": "waitlist-event-1"
    })
    assert reg2_response.status_code == 201
    assert reg2_response.json()["status"] == "confirmed"
    
    # Step 5: Register third user (should be waitlisted - event at capacity)
    mock_db.get_user.return_value = user3_data
    mock_db.count_confirmed_registrations.return_value = 2  # At capacity
    mock_db.create_registration.return_value = {
        "userId": "waitlist-user-3",
        "eventId": "waitlist-event-1",
        "status": "waitlisted",
        "registeredAt": "2024-12-03T10:10:00Z"
    }
    
    reg3_response = client.post("/registrations", json={
        "userId": "waitlist-user-3",
        "eventId": "waitlist-event-1"
    })
    assert reg3_response.status_code == 201
    assert reg3_response.json()["status"] == "waitlisted"
    
    # Step 6: Unregister first confirmed user
    mock_db.get_registration.return_value = {
        "userId": "waitlist-user-1",
        "eventId": "waitlist-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }
    mock_db.get_event.return_value = event_data
    mock_db.get_first_waitlisted_user.return_value = {
        "userId": "waitlist-user-3",
        "eventId": "waitlist-event-1",
        "status": "waitlisted",
        "registeredAt": "2024-12-03T10:10:00Z"
    }
    mock_db.delete_registration.return_value = True
    mock_db.update_registration_status.return_value = {
        "userId": "waitlist-user-3",
        "eventId": "waitlist-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:10:00Z"
    }
    
    delete_response = client.delete("/registrations/waitlist-user-1/waitlist-event-1")
    assert delete_response.status_code == 200
    
    # Step 7: Verify promotion occurred
    # The waitlisted user should now be confirmed
    mock_db.update_registration_status.assert_called_once_with(
        "waitlist-user-3",
        "waitlist-event-1",
        "confirmed"
    )


def test_user_viewing_registrations(mock_db):
    """
    Integration test for user viewing registrations
    Requirements: 5.1, 5.2, 5.3
    """
    # Step 1: Create a user
    user_data = {
        "userId": "multi-reg-user",
        "name": "Multi Registration User"
    }
    mock_db.create_user.return_value = user_data
    
    user_response = client.post("/users", json=user_data)
    assert user_response.status_code == 201
    
    # Step 2: Create multiple events
    event1_data = {
        "eventId": "multi-event-1",
        "title": "First Event",
        "description": "First event description",
        "date": "2024-12-20",
        "location": "Location 1",
        "capacity": 100,
        "organizer": "Organizer 1",
        "status": "active",
        "hasWaitlist": False
    }
    
    event2_data = {
        "eventId": "multi-event-2",
        "title": "Second Event",
        "description": "Second event description",
        "date": "2024-12-21",
        "location": "Location 2",
        "capacity": 50,
        "organizer": "Organizer 2",
        "status": "active",
        "hasWaitlist": True
    }
    
    event3_data = {
        "eventId": "multi-event-3",
        "title": "Third Event",
        "description": "Third event description",
        "date": "2024-12-22",
        "location": "Location 3",
        "capacity": 10,
        "organizer": "Organizer 3",
        "status": "scheduled",
        "hasWaitlist": True
    }
    
    # Step 3: Register for multiple events with different statuses
    mock_db.get_user.return_value = user_data
    
    # Register for event 1 (confirmed)
    mock_db.get_event.return_value = event1_data
    mock_db.count_confirmed_registrations.return_value = 0
    mock_db.create_registration.return_value = {
        "userId": "multi-reg-user",
        "eventId": "multi-event-1",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:00:00Z"
    }
    
    reg1_response = client.post("/registrations", json={
        "userId": "multi-reg-user",
        "eventId": "multi-event-1"
    })
    assert reg1_response.status_code == 201
    assert reg1_response.json()["status"] == "confirmed"
    
    # Register for event 2 (confirmed)
    mock_db.get_event.return_value = event2_data
    mock_db.count_confirmed_registrations.return_value = 10
    mock_db.create_registration.return_value = {
        "userId": "multi-reg-user",
        "eventId": "multi-event-2",
        "status": "confirmed",
        "registeredAt": "2024-12-03T10:05:00Z"
    }
    
    reg2_response = client.post("/registrations", json={
        "userId": "multi-reg-user",
        "eventId": "multi-event-2"
    })
    assert reg2_response.status_code == 201
    assert reg2_response.json()["status"] == "confirmed"
    
    # Register for event 3 (waitlisted - event at capacity)
    mock_db.get_event.return_value = event3_data
    mock_db.count_confirmed_registrations.return_value = 10  # At capacity
    mock_db.create_registration.return_value = {
        "userId": "multi-reg-user",
        "eventId": "multi-event-3",
        "status": "waitlisted",
        "registeredAt": "2024-12-03T10:10:00Z"
    }
    
    reg3_response = client.post("/registrations", json={
        "userId": "multi-reg-user",
        "eventId": "multi-event-3"
    })
    assert reg3_response.status_code == 201
    assert reg3_response.json()["status"] == "waitlisted"
    
    # Step 4: List all registrations for the user
    mock_db.list_user_registrations.return_value = [
        {
            "userId": "multi-reg-user",
            "eventId": "multi-event-1",
            "status": "confirmed",
            "registeredAt": "2024-12-03T10:00:00Z"
        },
        {
            "userId": "multi-reg-user",
            "eventId": "multi-event-2",
            "status": "confirmed",
            "registeredAt": "2024-12-03T10:05:00Z"
        },
        {
            "userId": "multi-reg-user",
            "eventId": "multi-event-3",
            "status": "waitlisted",
            "registeredAt": "2024-12-03T10:10:00Z"
        }
    ]
    
    # Mock get_event calls for building UserRegistration responses
    def mock_get_event_side_effect(event_id):
        if event_id == "multi-event-1":
            return event1_data
        elif event_id == "multi-event-2":
            return event2_data
        elif event_id == "multi-event-3":
            return event3_data
        return None
    
    mock_db.get_event.side_effect = mock_get_event_side_effect
    
    list_response = client.get("/users/multi-reg-user/registrations")
    assert list_response.status_code == 200
    
    # Step 5: Verify all registrations are present with correct details
    registrations = list_response.json()
    assert len(registrations) == 3
    
    # Verify first registration (confirmed)
    reg1 = next((r for r in registrations if r["eventId"] == "multi-event-1"), None)
    assert reg1 is not None
    assert reg1["eventTitle"] == "First Event"
    assert reg1["status"] == "confirmed"
    assert reg1["registeredAt"] == "2024-12-03T10:00:00Z"
    
    # Verify second registration (confirmed)
    reg2 = next((r for r in registrations if r["eventId"] == "multi-event-2"), None)
    assert reg2 is not None
    assert reg2["eventTitle"] == "Second Event"
    assert reg2["status"] == "confirmed"
    assert reg2["registeredAt"] == "2024-12-03T10:05:00Z"
    
    # Verify third registration (waitlisted)
    reg3 = next((r for r in registrations if r["eventId"] == "multi-event-3"), None)
    assert reg3 is not None
    assert reg3["eventTitle"] == "Third Event"
    assert reg3["status"] == "waitlisted"
    assert reg3["registeredAt"] == "2024-12-03T10:10:00Z"
