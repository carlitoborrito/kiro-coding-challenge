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
