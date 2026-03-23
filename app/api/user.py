from fastapi import APIRouter, HTTPException, status, Depends, Form
from typing import Dict, List, Any
from app.service.services import interest_service, event_service, event_service
from app.dependencies import get_current_user

router = APIRouter(tags=["user"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "User service is healthy"}

@router.get("/interests", response_model=Dict[str, Any])
async def get_interests():
    """Get all available interests"""
    interests = interest_service.get_all_interests()

    # Flatten the interests dict into a single list
    all_interests = []
    for category, items in interests.items():
        all_interests.extend(items)

    return {
        "message": "Interests retrieved successfully",
        "interests": list(set(all_interests))
    }

@router.post("/addInterests", response_model=Dict[str, Any])
async def add_interests(
    interests: List[str] = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Add interests for current user"""
    user_interests = interest_service.add_user_interests(current_user["id"], interests)

    if not user_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has interests"
        )

    return {
        "message": "Interests added successfully",
        "userInterests": user_interests
    }

@router.get("/interestedEvents", response_model=Dict[str, Any])
async def get_interested_events(current_user: Dict = Depends(get_current_user)):
    """Get events based on user interests"""
    events = interest_service.get_interested_events(current_user["id"])

    if not events:
        return {
            "message": "No interested events found for this user",
            "events": []
        }

    return {
        "message": "User interested events retrieved successfully",
        "events": events
    }

@router.get("/events/{eventId}", response_model=Dict[str, Any])
async def get_event_by_path(eventId: int):
    """Get event by ID in path (legacy compatibility or more RESTful path)"""
    event = event_service.get_event(eventId)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return {"event": event}
