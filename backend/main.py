from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv
from mangum import Mangum

from models import Event, EventCreate, EventUpdate, User, UserCreate, Registration, RegistrationCreate, EventRegistrationCreate, UserRegistration
from database import db_client

load_dotenv()

app = FastAPI(
    title="Events API",
    description="REST API for managing events with DynamoDB",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )


@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    """Create a new event"""
    try:
        event_data = event.model_dump()
        created_event = db_client.create_event(event_data)
        return created_event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/events", response_model=List[Event])
def list_events(status: Optional[str] = None):
    """List all events, optionally filtered by status"""
    try:
        events = db_client.list_events(status_filter=status)
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID"""
    try:
        event = db_client.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event"""
    try:
        # Check if event exists
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Only include fields that were provided
        update_data = event_update.model_dump(exclude_unset=True)
        updated_event = db_client.update_event(event_id, update_data)
        
        return updated_event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Delete an event"""
    try:
        # Check if event exists
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        db_client.delete_event(event_id)
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# User Management Endpoints

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_data = user.model_dump()
        created_user = db_client.create_user(user_data)
        return created_user
    except ValueError as e:
        # Handle duplicate userId error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/users/{userId}", response_model=User)
def get_user(userId: str):
    """Get a specific user by userId"""
    try:
        user = db_client.get_user(userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {userId} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Registration Management Endpoints

@app.post("/registrations", response_model=Registration, status_code=status.HTTP_201_CREATED)
def create_registration(registration: RegistrationCreate):
    """Register a user for an event"""
    try:
        # Verify user exists
        user = db_client.get_user(registration.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {registration.userId} not found"
            )
        
        # Verify event exists
        event = db_client.get_event(registration.eventId)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {registration.eventId} not found"
            )
        
        # Count confirmed registrations for the event
        confirmed_count = db_client.count_confirmed_registrations(registration.eventId)
        
        # Determine registration status based on capacity
        event_capacity = event.get('capacity', 0)
        has_waitlist = event.get('hasWaitlist', False)
        
        if confirmed_count < event_capacity:
            # Capacity available - confirmed status
            registration_status = "confirmed"
        elif has_waitlist:
            # Event full but has waitlist - waitlisted status
            registration_status = "waitlisted"
        else:
            # Event full and no waitlist - reject registration
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event {registration.eventId} is full and has no waitlist"
            )
        
        # Create registration
        registration_data = {
            'userId': registration.userId,
            'eventId': registration.eventId,
            'status': registration_status
        }
        created_registration = db_client.create_registration(registration_data)
        
        return created_registration
    except ValueError as e:
        # Handle duplicate registration error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/registrations/{userId}/{eventId}")
def delete_registration(userId: str, eventId: str):
    """Unregister a user from an event"""
    try:
        # Verify registration exists
        registration = db_client.get_registration(userId, eventId)
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration not found for user {userId} and event {eventId}"
            )
        
        # Get registration status
        registration_status = registration.get('status')
        
        # Verify event exists (for waitlist check)
        event = db_client.get_event(eventId)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {eventId} not found"
            )
        
        # Delete the registration
        db_client.delete_registration(userId, eventId)
        
        # If user was confirmed and event has waitlist, promote first waitlisted user
        if registration_status == 'confirmed' and event.get('hasWaitlist', False):
            first_waitlisted = db_client.get_first_waitlisted_user(eventId)
            if first_waitlisted:
                db_client.update_registration_status(
                    first_waitlisted['userId'],
                    eventId,
                    'confirmed'
                )
        
        return {"message": "Registration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/users/{userId}/registrations", response_model=List[UserRegistration])
def list_user_registrations(userId: str):
    """List all registrations for a user with event details"""
    try:
        # Verify user exists
        user = db_client.get_user(userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {userId} not found"
            )
        
        # Get all registrations for the user
        registrations = db_client.list_user_registrations(userId)
        
        # Build UserRegistration response objects with event details
        user_registrations = []
        for registration in registrations:
            event = db_client.get_event(registration['eventId'])
            if event:  # Only include if event still exists
                user_registration = {
                    'eventId': registration['eventId'],
                    'eventTitle': event.get('title', ''),
                    'status': registration['status'],
                    'registeredAt': registration['registeredAt']
                }
                user_registrations.append(user_registration)
        
        return user_registrations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Event-based Registration Endpoints (alternative paths)

@app.post("/events/{eventId}/registrations", response_model=Registration, status_code=status.HTTP_201_CREATED)
def create_event_registration(eventId: str, registration: EventRegistrationCreate):
    """Register a user for an event (eventId from path)"""
    try:
        # Verify user exists
        user = db_client.get_user(registration.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {registration.userId} not found"
            )
        
        # Verify event exists
        event = db_client.get_event(eventId)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {eventId} not found"
            )
        
        # Count confirmed registrations for the event
        confirmed_count = db_client.count_confirmed_registrations(eventId)
        
        # Determine registration status based on capacity
        event_capacity = event.get('capacity', 0)
        has_waitlist = event.get('hasWaitlist', False)
        
        if confirmed_count < event_capacity:
            # Capacity available - confirmed status
            registration_status = "confirmed"
        elif has_waitlist:
            # Event full but has waitlist - waitlisted status
            registration_status = "waitlisted"
        else:
            # Event full and no waitlist - reject registration
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event {eventId} is full and has no waitlist"
            )
        
        # Create registration
        registration_data = {
            'userId': registration.userId,
            'eventId': eventId,
            'status': registration_status
        }
        created_registration = db_client.create_registration(registration_data)
        
        return created_registration
    except ValueError as e:
        # Handle duplicate registration error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/events/{eventId}/registrations", response_model=List[Registration])
def list_event_registrations(eventId: str, status: Optional[str] = None):
    """List all registrations for an event"""
    try:
        # Verify event exists
        event = db_client.get_event(eventId)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {eventId} not found"
            )
        
        # Get all registrations for the event
        registrations = db_client.list_event_registrations(eventId, status)
        
        return registrations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/events/{eventId}/registrations/{userId}")
def delete_event_registration(eventId: str, userId: str):
    """Unregister a user from an event (alternative path)"""
    try:
        # Verify registration exists
        registration = db_client.get_registration(userId, eventId)
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration not found for user {userId} and event {eventId}"
            )
        
        # Get registration status
        registration_status = registration.get('status')
        
        # Verify event exists (for waitlist check)
        event = db_client.get_event(eventId)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {eventId} not found"
            )
        
        # Delete the registration
        db_client.delete_registration(userId, eventId)
        
        # If user was confirmed and event has waitlist, promote first waitlisted user
        if registration_status == 'confirmed' and event.get('hasWaitlist', False):
            first_waitlisted = db_client.get_first_waitlisted_user(eventId)
            if first_waitlisted:
                db_client.update_registration_status(
                    first_waitlisted['userId'],
                    eventId,
                    'confirmed'
                )
        
        return {"message": "Registration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Lambda handler
handler = Mangum(app)
