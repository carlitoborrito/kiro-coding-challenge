from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RegistrationStatus(str, Enum):
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    date: str = Field(..., description="ISO format date string or YYYY-MM-DD")
    location: str = Field(..., min_length=1, max_length=200)
    capacity: int = Field(..., gt=0, le=100000)
    organizer: str = Field(..., min_length=1, max_length=100)
    status: EventStatus = EventStatus.ACTIVE
    hasWaitlist: bool = Field(default=False)
    waitlistEnabled: Optional[bool] = Field(default=None, exclude=True)

    @model_validator(mode='after')
    def sync_waitlist_fields(self):
        # Support both hasWaitlist and waitlistEnabled
        if self.waitlistEnabled is not None:
            self.hasWaitlist = self.waitlistEnabled
        return self

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            # Try ISO format first
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            # Try simple date format YYYY-MM-DD
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in ISO format or YYYY-MM-DD')


class EventCreate(EventBase):
    eventId: Optional[str] = None  # Allow custom eventId


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0, le=100000)
    organizer: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[EventStatus] = None
    hasWaitlist: Optional[bool] = None
    waitlistEnabled: Optional[bool] = Field(default=None, exclude=True)

    @model_validator(mode='after')
    def sync_waitlist_fields(self):
        # Support both hasWaitlist and waitlistEnabled
        if self.waitlistEnabled is not None:
            self.hasWaitlist = self.waitlistEnabled
        return self

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
                return v
            except ValueError:
                raise ValueError('Date must be in ISO format')
        return v


class Event(EventBase):
    eventId: str

    class Config:
        from_attributes = True


# User Models

class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or v.strip() == '':
            raise ValueError('Name cannot be empty or whitespace only')
        return v


class User(BaseModel):
    userId: str
    name: str

    class Config:
        from_attributes = True


# Registration Models

class RegistrationCreate(BaseModel):
    userId: str
    eventId: str


class EventRegistrationCreate(BaseModel):
    """Registration model for event-specific endpoint (eventId comes from path)"""
    userId: str


class Registration(BaseModel):
    userId: str
    eventId: str
    status: RegistrationStatus
    registeredAt: str  # ISO timestamp

    class Config:
        from_attributes = True


class UserRegistration(BaseModel):
    eventId: str
    eventTitle: str
    status: RegistrationStatus
    registeredAt: str

    class Config:
        from_attributes = True
