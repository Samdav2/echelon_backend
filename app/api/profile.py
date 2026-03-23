from fastapi import APIRouter, HTTPException, status, Depends, Form
from typing import Dict, Any
from app.service.services import profile_service
from app.dependencies import get_current_user
from app.schema import CreatorProfileCreate, UserProfileCreate

router = APIRouter(tags=["profile"])

@router.post("/creatorProfile", response_model=Dict[str, Any])
async def create_creator_profile(
    name: str = Form(...),
    phone_no: str = Form(...),
    address: str = Form(...),
    brand_name: str = Form(...),
    email: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Create a creator profile"""
    profile_data = {
        "user_id": current_user["id"],
        "name": name,
        "phone_no": phone_no,
        "address": address,
        "brand_name": brand_name,
        "email": email
    }

    profile = profile_service.create_creator_profile(profile_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile"
        )

    return {
        "message": "Profile created successfully",
        "userInfo": profile
    }

@router.post("/userProfile", response_model=Dict[str, Any])
async def create_user_profile(
    name: str = Form(...),
    phone_no: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Create a user profile"""
    profile_data = {
        "user_id": current_user["id"],
        "name": name,
        "phone_no": phone_no,
        "address": address,
        "email": email
    }

    profile = profile_service.create_user_profile(profile_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile"
        )

    return {
        "message": "Profile created successfully",
        "userInfo": profile
    }

@router.get("/getProfile", response_model=Dict[str, Any])
async def get_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user profile"""
    import logging
    user_id = current_user.get("id")
    logging.info(f"Fetching profile for user_id: {user_id}")

    profile = profile_service.get_profile(user_id)

    if not profile:
        logging.info(f"No profile found for user_id: {user_id}, returning user info")
        # Return user info if no profile exists yet
        return {
            "id": current_user.get("id"),
            "user_id": current_user.get("id"),
            "name": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "phoneno": None,
            "address": None,
            "profile_picture": None
        }

    return profile


@router.put("/updateuser", response_model=Dict[str, Any])
async def update_user_profile(
    name: str = Form(...),
    phone_no: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Update the current user's attendee profile"""
    profile_data = {
        "user_id": current_user["id"],
        "name": name,
        "phone_no": phone_no,
        "address": address,
        "email": email,
    }

    updated = profile_service.update_user_profile(profile_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile not found or update failed",
        )

    return {
        "message": "Profile updated successfully",
        "updatedUser": updated,
    }


@router.put("/updatecreator", response_model=Dict[str, Any])
async def update_creator_profile(
    name: str = Form(...),
    phone_no: str = Form(...),
    address: str = Form(...),
    brand_name: str = Form(...),
    email: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Update the current user's creator profile"""
    profile_data = {
        "user_id": current_user["id"],
        "name": name,
        "phone_no": phone_no,
        "address": address,
        "brand_name": brand_name,
        "email": email,
    }

    updated = profile_service.update_creator_profile(profile_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator profile not found or update failed",
        )

    return {
        "message": "Creator Profile updated successfully",
        "updatedUser": updated,
    }
