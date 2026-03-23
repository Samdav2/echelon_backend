"""
SQLAlchemy ORM Models Package

This package contains all database models using SQLAlchemy ORM.
Models are industry-standard with proper relationships, constraints, and indexing.

Included Models:
- UserCredential: User authentication credentials
- CreatorProfile: Event creator/organizer profiles
- UserProfile: Regular user profiles
- EventCreation: Event details and management
- TableCategory: Table categories for events
- UserEvent: Ticket/attendance records
- UserInterest: User interests for event filtering
"""

from app.models.models import (
    Base,
    UserCredential,
    CreatorProfile,
    UserProfile,
    EventCreation,
    TableCategory,
    UserEvent,
    UserInterest,
)

__all__ = [
    'Base',
    'UserCredential',
    'CreatorProfile',
    'UserProfile',
    'EventCreation',
    'TableCategory',
    'UserEvent',
    'UserInterest',
]
