"""
Pydantic Schema Models

Validation schemas for request/response handling using Pydantic v2.
All schemas include proper validation and documentation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, AliasChoices
from typing import Optional, List, Any
from datetime import datetime, date as date_type, time
from decimal import Decimal

# ============ User Credential Models ============

class UserCredentialBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=255, description="Username for login")

class UserCredentialCreate(UserCredentialBase):
    password: str = Field(..., min_length=8, max_length=255, description="Password (min 8 characters)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserCredentialUpdate(BaseModel):
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserCredential(UserCredentialBase):
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Account status")

    model_config = ConfigDict(from_attributes=True)

# ============ Creator Profile Models ============

class CreatorProfileBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Creator full name")
    phoneno: Optional[str] = Field(None, max_length=255, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address")
    brandname: Optional[str] = Field(None, max_length=255, description="Brand/organization name")
    email: EmailStr = Field(..., description="Email address")
    bio: Optional[str] = Field(None, description="Creator biography")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")

class CreatorProfileCreate(CreatorProfileBase):
    user_id: int = Field(..., description="User ID reference")

class CreatorProfileUpdate(BaseModel):
    name: Optional[str] = None
    phoneno: Optional[str] = None
    address: Optional[str] = None
    brandname: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class CreatorProfile(CreatorProfileBase):
    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID reference")
    username: Optional[str] = Field(None, description="Username from user credentials")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

# ============ User Profile Models ============

class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="User full name")
    phoneno: Optional[str] = Field(None, max_length=255, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address")
    email: EmailStr = Field(..., description="Email address")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")

class UserProfileCreate(UserProfileBase):
    user_id: int = Field(..., description="User ID reference")

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phoneno: Optional[str] = None
    address: Optional[str] = None
    profile_picture: Optional[str] = None

class UserProfile(UserProfileBase):
    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID reference")
    username: Optional[str] = Field(None, description="Username from user credentials")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

# ============ Event Models ============

class EventBase(BaseModel):
    brand_name: Optional[str] = Field(None, max_length=255, description="Brand organizing event")
    event_name: str = Field(..., min_length=2, max_length=255, description="Event title")
    event_address: str = Field(..., description="Event venue address")
    time_in: Optional[time] = Field(None, description="Event start time")
    time_out: Optional[time] = Field(None, description="Event end time")
    summary: Optional[str] = Field(None, description="Event description")
    category: str = Field(..., description="Event category")
    date: date_type = Field(..., description="Event date")
    price: Optional[Decimal] = Field(None, ge=0, description="Regular ticket price")

class EventCreate(EventBase):
    creator_id: Optional[int] = Field(None, description="Creator profile ID")
    picture: Optional[str] = Field(None, description="Event image URL")
    account_name: Optional[str] = Field(None, description="Bank account holder name")
    account_number: Optional[str] = Field(None, description="Bank account number")
    bank: Optional[str] = Field(None, description="Bank name")
    vip_price: Optional[Decimal] = Field(None, ge=0, description="VIP ticket price")
    vvip_price: Optional[Decimal] = Field(None, ge=0, description="VVIP ticket price")
    vvvip_price: Optional[Decimal] = Field(None, ge=0, description="VVVIP ticket price")
    table_price: Optional[Decimal] = Field(None, ge=0, description="Table price")

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    event_address: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date_type] = None
    price: Optional[Decimal] = None
    vip_price: Optional[Decimal] = None
    vvip_price: Optional[Decimal] = None
    vvvip_price: Optional[Decimal] = None
    table_price: Optional[Decimal] = None

class Event(EventBase):
    id: int = Field(..., description="Event ID")
    creator_id: Optional[int] = None
    picture: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    bank: Optional[str] = None
    vip_price: Optional[Decimal] = None
    vvip_price: Optional[Decimal] = None
    vvvip_price: Optional[Decimal] = None
    table_price: Optional[Decimal] = None
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Event status")

    model_config = ConfigDict(from_attributes=True)


# ============ Table Category Models ============

class TableCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Table category name")
    capacity: int = Field(..., gt=0, description="Seating capacity")
    price: Decimal = Field(..., ge=0, description="Price per table")
    available_tables: int = Field(default=0, ge=0, description="Available tables")

class TableCategoryCreate(TableCategoryBase):
    event_id: int = Field(..., description="Event ID reference")

class TableCategoryUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[Decimal] = None
    available_tables: Optional[int] = None

class TableCategory(TableCategoryBase):
    id: int = Field(..., description="Table category ID")
    event_id: int = Field(..., description="Event ID reference")
    event_name: str = Field(..., description="Event name")
    is_active: bool = Field(default=True, description="Whether the table category is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============ Table Category Request Models (Frontend Specific) ============

class TableCreationItem(BaseModel):
    tableName: str = Field(..., min_length=1, max_length=50, alias="name")
    tablePrice: Decimal = Field(..., ge=0, alias="price")
    tableCapacity: int = Field(..., gt=0, alias="capacity")
    available_tables: Optional[int] = Field(0, ge=0)

    model_config = ConfigDict(populate_by_name=True)

class TableCreationRequest(BaseModel):
    event_id: int = Field(..., description="Event ID reference")
    tables: List[TableCreationItem] = Field(..., description="List of table categories to create")

class TableUpdateItem(BaseModel):
    id: int = Field(..., description="Unique ID of the table category to update")
    tableName: Optional[str] = Field(None, max_length=50, alias="name")
    tablePrice: Optional[Decimal] = Field(None, ge=0, alias="price")
    tableCapacity: Optional[int] = Field(None, gt=0, alias="capacity")
    available_tables: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(populate_by_name=True)

class TableUpdateRequest(BaseModel):
    tables: List[TableUpdateItem] = Field(..., description="List of table categories to update")


# ============ User Event / Ticket Models ============

class UserEventBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    event_id: int = Field(..., description="Event ID")
    ticket_type: Optional[str] = Field(None, max_length=50, description="Ticket type (Regular, VIP, etc)")

class UserEventCreate(UserEventBase):
    email: Optional[str] = Field(None, description="Email address")
    qrcode_url: Optional[str] = Field(None, description="QR code URL")

class UserEventUpdate(BaseModel):
    ticket_type: Optional[str] = None
    isVerified: Optional[bool] = None

class UserEvent(UserEventBase):
    id: int = Field(..., description="Ticket ID")
    attended_at: datetime = Field(..., description="Purchase timestamp")
    email: Optional[str] = None
    qrcode_url: Optional[str] = None
    token: Optional[str] = Field(None, description="Verification token")
    isVerified: bool = Field(default=False, description="Verification status")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============ Ticket Response Models ============

class TicketResponse(BaseModel):
    token: str = Field(..., description="Verification token")
    qrcode_url: Optional[str] = None
    ticket_type: Optional[str] = None
    event_name: str = Field(..., description="Event name")
    event_date: date_type = Field(..., description="Event date")
    event_time: Optional[time] = None
    email: Optional[str] = None


# ============ Attendee Response Models ============

class AttendeeResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    email: Optional[str] = None
    ticket_type: Optional[str] = None
    attended_at: datetime = Field(..., description="Attendance timestamp")
    isVerified: bool = Field(default=False, description="Verification status")

# ============ User Interests Models ============

class UserInterestBase(BaseModel):
    interests: List[str] = Field(default_factory=list, description="List of interest categories")

class UserInterestCreate(UserInterestBase):
    user_id: int = Field(..., description="User ID")

class UserInterestUpdate(BaseModel):
    interests: List[str] = Field(..., description="Updated interests list")

class UserInterest(UserInterestBase):
    id: int = Field(..., description="Interest record ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

# ============ Authentication Models ============

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    profile_type: Optional[str] = Field(None, description="Profile type (creator/user)")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    profile: Optional[dict] = Field(None, description="User profile data")
    user_id: Optional[int] = Field(None, description="User ID")

class VerificationCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="Email to send code to")

class VerifyCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    code: str = Field(..., min_length=4, max_length=10, description="Verification code")
    username: Optional[str] = Field(None, description="Username for signup")
    password: Optional[str] = Field(None, description="Password for signup")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    new_password: str = Field(..., min_length=8, description="New password", validation_alias=AliasChoices('new_password', 'newPassword', 'password'))

class PasswordResetVerifyRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    code: str = Field(..., description="Verification code")
    new_password: str = Field(..., min_length=8, description="New password", validation_alias=AliasChoices('new_password', 'newPassword', 'password'))


# ============ Interest Models ============

class InterestResponse(BaseModel):
    interests: List[str] = Field(..., description="List of available interests")

class UserInterestedEventsResponse(BaseModel):
    events: List[Event] = Field(..., description="List of events matching interests")
    total: int = Field(..., description="Total events found")


# ============ Generic Response Models ============

class SuccessResponse(BaseModel):
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")

class PaginatedResponse(BaseModel):
    """Generic paginated response model"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total items count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total pages")


# ============ Backwards Compatibility Aliases ============
# These aliases maintain compatibility with existing code

# ============ Backwards Compatibility Aliases ============

UserCreate = UserCredentialCreate
User = UserCredential

# ============ Exports ============

__all__ = [
    # User Credential Models
    "UserCredentialBase",
    "UserCredentialCreate",
    "UserCreate",
    "UserCredentialUpdate",
    "UserCredential",
    "User",

    # Creator Profile Models
    "CreatorProfileBase",
    "CreatorProfileCreate",
    "CreatorProfileUpdate",
    "CreatorProfile",

    # User Profile Models
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfile",

    # Event Models
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "Event",

    # Table Category Models
    "TableCategoryBase",
    "TableCategoryCreate",
    "TableCategoryUpdate",
    "TableCategory",
    "TableCreationItem",
    "TableCreationRequest",
    "TableUpdateItem",
    "TableUpdateRequest",

    # User Event / Ticket Models
    "UserEventBase",
    "UserEventCreate",
    "UserEventUpdate",
    "UserEvent",
    "TicketResponse",
    "AttendeeResponse",

    # User Interests Models
    "UserInterestBase",
    "UserInterestCreate",
    "UserInterestUpdate",
    "UserInterest",

    # Authentication Models
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "VerificationCodeRequest",
    "VerifyCodeRequest",
    "ResetPasswordRequest",
    "PasswordResetVerifyRequest",

    # Interest Models
    "InterestResponse",
    "UserInterestedEventsResponse",

    # Generic Response Models
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
