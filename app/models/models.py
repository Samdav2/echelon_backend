"""
SQLAlchemy ORM Models for Ticket Booking System
Industry-standard database models with proper relationships and constraints
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Time,
    Boolean, ForeignKey, JSON, Index, UniqueConstraint,
    CheckConstraint, TIMESTAMP, text, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class UserCredential(Base):
    """
    User authentication credentials table
    Stores login information for all users
    """
    __tablename__ = "user_credential"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique user identifier"
    )
    username = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique username for login"
    )
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique email address"
    )
    password = Column(
        String(255),
        nullable=False,
        comment="Hashed password using bcrypt"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Account creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account status flag"
    )

    # Relationships
    creator_profile = relationship(
        "CreatorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="CreatorProfile.user_id"
    )
    user_profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="UserProfile.user_id"
    )
    user_events = relationship(
        "UserEvent",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    user_interests = relationship(
        "UserInterest",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_username', 'username'),
    )


class CreatorProfile(Base):
    """
    Creator/Event organizer profile information
    Extended profile for users who create and manage events
    """
    __tablename__ = "creatorprofile"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Creator profile unique identifier"
    )
    user_id = Column(
        Integer,
        ForeignKey("user_credential.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Reference to user_credential"
    )
    name = Column(
        String(255),
        nullable=False,
        comment="Creator's full name"
    )
    phoneno = Column(
        String(255),
        nullable=True,
        comment="Creator's contact phone number"
    )
    address = Column(
        Text,
        nullable=True,
        comment="Creator's physical address"
    )
    brandname = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Brand or organization name"
    )
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Creator's email address"
    )
    bio = Column(
        Text,
        nullable=True,
        comment="Creator biography"
    )
    profile_picture = Column(
        String(500),
        nullable=True,
        comment="URL to profile picture"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Profile creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    user = relationship("UserCredential", back_populates="creator_profile")
    events = relationship(
        "EventCreation",
        back_populates="creator",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_creator_user_id', 'user_id'),
        Index('idx_creator_email', 'email'),
        Index('idx_creator_brandname', 'brandname'),
    )


class UserProfile(Base):
    """
    Regular user profile information
    Extended profile for users who attend events
    """
    __tablename__ = "userprofiles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="User profile unique identifier"
    )
    user_id = Column(
        Integer,
        ForeignKey("user_credential.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Reference to user_credential"
    )
    name = Column(
        String(255),
        nullable=False,
        comment="User's full name"
    )
    phoneno = Column(
        String(255),
        nullable=True,
        comment="User's contact phone number"
    )
    address = Column(
        Text,
        nullable=True,
        comment="User's physical address"
    )
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="User's email address"
    )
    profile_picture = Column(
        String(500),
        nullable=True,
        comment="URL to profile picture"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Profile creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    user = relationship("UserCredential", back_populates="user_profile")

    __table_args__ = (
        Index('idx_user_profile_user_id', 'user_id'),
        Index('idx_user_profile_email', 'email'),
    )


class EventCreation(Base):
    """
    Event creation and management table
    Stores all event details including pricing tiers and bank information
    """
    __tablename__ = "eventcreation"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Event unique identifier"
    )
    creator_id = Column(
        Integer,
        ForeignKey("creatorprofile.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reference to creator profile"
    )
    brand_name = Column(
        String(255),
        nullable=True,
        comment="Brand organizing the event"
    )
    event_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Event title/name"
    )
    event_address = Column(
        String(255),
        nullable=False,
        comment="Event venue address"
    )
    time_in = Column(
        Time,
        nullable=True,
        comment="Event start time"
    )
    time_out = Column(
        Time,
        nullable=True,
        comment="Event end time"
    )
    summary = Column(
        Text,
        nullable=True,
        comment="Event description and details"
    )
    picture = Column(
        String(500),
        nullable=True,
        comment="Path to event promotional image"
    )
    price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Regular ticket price"
    )
    category = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Event category (concert, conference, etc)"
    )
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Event date"
    )

    # Bank account information
    account_name = Column(
        String(255),
        nullable=True,
        comment="Bank account holder name"
    )
    account_number = Column(
        String(255),
        nullable=True,
        comment="Bank account number"
    )
    bank = Column(
        String(255),
        nullable=True,
        comment="Bank name"
    )

    # Pricing tiers
    vip_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="VIP ticket price"
    )
    vvip_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="VVIP ticket price"
    )
    vvvip_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="VVVIP ticket price"
    )
    table_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Table reservation price"
    )

    # Metadata
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Event creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Event availability status"
    )

    # Relationships
    creator = relationship("CreatorProfile", back_populates="events")
    user_events = relationship(
        "UserEvent",
        back_populates="event",
        cascade="all, delete-orphan"
    )
    table_categories = relationship(
        "TableCategory",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_event_name', 'event_name'),
        Index('idx_event_category', 'category'),
        Index('idx_event_date', 'date'),
        Index('idx_event_creator_id', 'creator_id'),
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('vip_price >= 0', name='check_vip_price_positive'),
        CheckConstraint('vvip_price >= 0', name='check_vvip_price_positive'),
        CheckConstraint('vvvip_price >= 0', name='check_vvvip_price_positive'),
        CheckConstraint('table_price >= 0', name='check_table_price_positive'),
    )


class TableCategory(Base):
    """
    Table categories for events
    Manages different table types with capacity and pricing
    """
    __tablename__ = "table_categories"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Table category unique identifier"
    )
    event_id = Column(
        Integer,
        ForeignKey("eventcreation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to event"
    )
    name = Column(
        String(50),
        nullable=False,
        comment="Table category name (e.g., Standard, VIP)"
    )
    capacity = Column(
        Integer,
        nullable=False,
        comment="Number of seats at this table"
    )
    price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Price per table"
    )
    available_tables = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of available tables"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    event = relationship("EventCreation", back_populates="table_categories")

    __table_args__ = (
        Index('idx_table_event_id', 'event_id'),
        Index('idx_table_name', 'name'),
        CheckConstraint('capacity > 0', name='check_capacity_positive'),
        CheckConstraint('price >= 0', name='check_table_price_positive'),
        CheckConstraint('available_tables >= 0', name='check_available_tables_positive'),
    )


class UserEvent(Base):
    """
    User event attendance and ticket information
    Tracks user ticket purchases with QR codes and verification tokens
    """
    __tablename__ = "user_events"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Ticket record unique identifier"
    )
    user_id = Column(
        Integer,
        ForeignKey("user_credential.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to user"
    )
    event_id = Column(
        Integer,
        ForeignKey("eventcreation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to event"
    )
    attended_at = Column(
        TIMESTAMP,
        default=datetime.utcnow,
        nullable=False,
        comment="Ticket purchase timestamp"
    )
    email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email associated with ticket"
    )
    qrcode_url = Column(
        String(500),
        nullable=True,
        comment="QR code image URL"
    )
    token = Column(
        String(500),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique verification token for entry"
    )
    ticket_type = Column(
        String(50),
        nullable=True,
        comment="Ticket category (Regular, VIP, VVIP, etc)"
    )
    isVerified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Entry verification status"
    )
    verified_at = Column(
        DateTime,
        nullable=True,
        comment="Ticket verification timestamp"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Record creation timestamp"
    )

    # Relationships
    user = relationship("UserCredential", back_populates="user_events")
    event = relationship("EventCreation", back_populates="user_events")

    __table_args__ = (
        Index('idx_user_event_user_id', 'user_id'),
        Index('idx_user_event_event_id', 'event_id'),
        Index('idx_user_event_token', 'token'),
        Index('idx_user_event_email', 'email'),
    )


class UserInterest(Base):
    """
    User interest preferences for event filtering
    Stores user interests as JSON for flexible querying
    """
    __tablename__ = "user_interests"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="User interest record unique identifier"
    )
    user_id = Column(
        Integer,
        ForeignKey("user_credential.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Reference to user"
    )
    interests = Column(
        JSON,
        nullable=False,
        default=list,
        comment="List of interest categories as JSON array"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    user = relationship("UserCredential", back_populates="user_interests")

    __table_args__ = (
        Index('idx_user_interests_user_id', 'user_id'),
    )


# Export all models
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
