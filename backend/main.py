from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv
from mangum import Mangum

from models import Event, EventCreate, EventUpdate
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


# Lambda handler
handler = Mangum(app)
