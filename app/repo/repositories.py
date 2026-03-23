from typing import List, Optional, Dict, Any

from sqlalchemy import or_

from app.core.database import db
from app.core.orm import get_session
from app.models.models import (
    UserCredential,
    CreatorProfile,
    UserProfile,
    EventCreation,
    TableCategory,
    UserEvent,
    UserInterest,
)

class UserRepository:
    """User data access layer"""

    @staticmethod
    def create(username: str, email: str, password_hash: str) -> Optional[Dict]:
        """Create a new user"""
        with get_session() as session:
            user = UserCredential(
                username=username,
                email=email,
                password=password_hash,
            )
            session.add(user)
            session.flush()
            session.refresh(user)

            return UserRepository._to_dict(user)

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with get_session() as session:
            user = session.query(UserCredential).filter(UserCredential.id == user_id).first()
            return UserRepository._to_dict(user) if user else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        with get_session() as session:
            user = session.query(UserCredential).filter(UserCredential.email == email).first()
            return UserRepository._to_dict(user) if user else None

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        """Get user by username"""
        with get_session() as session:
            user = session.query(UserCredential).filter(UserCredential.username == username).first()
            return UserRepository._to_dict(user) if user else None

    @staticmethod
    def get_all() -> List[Dict]:
        """Get all users"""
        with get_session() as session:
            users = session.query(UserCredential).all()
            return [UserRepository._to_dict(user) for user in users]

    @staticmethod
    def update_password(email: str, password_hash: str) -> bool:
        """Update user password"""
        with get_session() as session:
            user = session.query(UserCredential).filter(UserCredential.email == email).first()
            if not user:
                return False

            user.password = password_hash
            session.add(user)
            return True

    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete user"""
        with get_session() as session:
            user = session.query(UserCredential).filter(UserCredential.id == user_id).first()
            if not user:
                return False

            session.delete(user)
            return True

    @staticmethod
    def _to_dict(user: UserCredential) -> Dict[str, Any]:
        """Convert a UserCredential ORM object to a plain dict."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active,
        }

class CreatorProfileRepository:
    """Creator Profile data access layer"""

    @staticmethod
    def create(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a creator profile"""
        with get_session() as session:
            profile = CreatorProfile(
                user_id=profile_data.get('user_id'),
                name=profile_data.get('name'),
                phoneno=profile_data.get('phone_no'),
                address=profile_data.get('address'),
                brandname=profile_data.get('brand_name'),
                email=profile_data.get('email'),
            )
            session.add(profile)
            session.flush()
            session.refresh(profile)

            return CreatorProfileRepository._to_dict(profile)

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Dict]:
        """Get creator profile by user ID"""
        with get_session() as session:
            profile = session.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
            return CreatorProfileRepository._to_dict(profile) if profile else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get creator profile by email"""
        with get_session() as session:
            profile = session.query(CreatorProfile).filter(CreatorProfile.email == email).first()
            return CreatorProfileRepository._to_dict(profile) if profile else None

    @staticmethod
    def exists(user_id: int, email: str) -> bool:
        """Check if creator profile exists"""
        with get_session() as session:
            exists = (
                session.query(CreatorProfile)
                .filter(or_(CreatorProfile.user_id == user_id, CreatorProfile.email == email))
                .first()
                is not None
            )
            return exists

    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete creator profile"""
        with get_session() as session:
            profile = session.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
            if not profile:
                return False

            session.delete(profile)
            return True

    @staticmethod
    def _to_dict(profile: CreatorProfile) -> Dict[str, Any]:
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "username": profile.user.username if profile.user else None,
            "name": profile.name,
            "phoneno": profile.phoneno,
            "address": profile.address,
            "brandname": profile.brandname,
            "email": profile.email,
            "bio": profile.bio,
            "profile_picture": profile.profile_picture,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

    @staticmethod
    def update(user_id: int, profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing creator profile by user_id"""
        with get_session() as session:
            profile = session.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
            if not profile:
                return None

            if profile_data.get('name') is not None:
                profile.name = profile_data.get('name')
            if profile_data.get('phone_no') is not None:
                profile.phoneno = profile_data.get('phone_no')
            if profile_data.get('address') is not None:
                profile.address = profile_data.get('address')
            if profile_data.get('brand_name') is not None:
                profile.brandname = profile_data.get('brand_name')
            if profile_data.get('email') is not None:
                profile.email = profile_data.get('email')

            session.add(profile)
            session.flush()
            session.refresh(profile)

            return CreatorProfileRepository._to_dict(profile)

class UserProfileRepository:
    """User Profile data access layer"""

    @staticmethod
    def create(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a user profile"""
        with get_session() as session:
            profile = UserProfile(
                user_id=profile_data.get('user_id'),
                name=profile_data.get('name'),
                phoneno=profile_data.get('phone_no'),
                address=profile_data.get('address'),
                email=profile_data.get('email'),
            )
            session.add(profile)
            session.flush()
            session.refresh(profile)

            return UserProfileRepository._to_dict(profile)

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Dict]:
        """Get user profile by user ID"""
        with get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            return UserProfileRepository._to_dict(profile) if profile else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get user profile by email"""
        with get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.email == email).first()
            return UserProfileRepository._to_dict(profile) if profile else None

    @staticmethod
    def exists(user_id: int, email: str) -> bool:
        """Check if user profile exists"""
        with get_session() as session:
            exists = (
                session.query(UserProfile)
                .filter(or_(UserProfile.user_id == user_id, UserProfile.email == email))
                .first()
                is not None
            )
            return exists

    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete user profile"""
        with get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                return False

            session.delete(profile)
            return True

    @staticmethod
    def _to_dict(profile: UserProfile) -> Dict[str, Any]:
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "username": profile.user.username if profile.user else None,
            "name": profile.name,
            "phoneno": profile.phoneno,
            "address": profile.address,
            "email": profile.email,
            "profile_picture": profile.profile_picture,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

    @staticmethod
    def update(user_id: int, profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing user profile by user_id"""
        with get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                return None

            if profile_data.get('name') is not None:
                profile.name = profile_data.get('name')
            if profile_data.get('phone_no') is not None:
                profile.phoneno = profile_data.get('phone_no')
            if profile_data.get('address') is not None:
                profile.address = profile_data.get('address')
            if profile_data.get('email') is not None:
                profile.email = profile_data.get('email')

            session.add(profile)
            session.flush()
            session.refresh(profile)

            return UserProfileRepository._to_dict(profile)

class EventRepository:
    """Event data access layer"""

    @staticmethod
    def create(event_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new event"""
        with get_session() as session:
            event = EventCreation(
                brand_name=event_data.get('brand_name'),
                event_name=event_data.get('event_name'),
                event_address=event_data.get('event_address'),
                time_in=event_data.get('time_in'),
                time_out=event_data.get('time_out'),
                summary=event_data.get('summary'),
                picture=event_data.get('picture'),
                price=event_data.get('price'),
                category=event_data.get('category'),
                date=event_data.get('date'),
                account_name=event_data.get('account_name'),
                account_number=event_data.get('account_number'),
                bank=event_data.get('bank'),
                vip_price=event_data.get('vip_price'),
                vvip_price=event_data.get('vvip_price'),
                vvvip_price=event_data.get('vvvip_price'),
                table_price=event_data.get('table_price'),
            )
            session.add(event)
            session.flush()
            session.refresh(event)

            return EventRepository._to_dict(event)

    @staticmethod
    def get_by_id(event_id: int) -> Optional[Dict]:
        """Get event by ID"""
        with get_session() as session:
            event = session.query(EventCreation).filter(EventCreation.id == event_id).first()
            return EventRepository._to_dict(event) if event else None

    @staticmethod
    def get_by_name(brand_name: str, event_name: str) -> Optional[Dict]:
        """Get event by brand and name"""
        with get_session() as session:
            event = (
                session.query(EventCreation)
                .filter(EventCreation.brand_name == brand_name, EventCreation.event_name == event_name)
                .first()
            )
            return EventRepository._to_dict(event) if event else None

    @staticmethod
    def get_all() -> List[Dict]:
        """Get all events"""
        with get_session() as session:
            events = session.query(EventCreation).all()
            return [EventRepository._to_dict(event) for event in events]

    @staticmethod
    def get_by_category(category: str) -> List[Dict]:
        """Get events by category"""
        with get_session() as session:
            events = session.query(EventCreation).filter(EventCreation.category == category).all()
            return [EventRepository._to_dict(event) for event in events]

    @staticmethod
    def get_by_brand(brand_name: str) -> List[Dict]:
        """Get events by brand/creator name"""
        with get_session() as session:
            events = session.query(EventCreation).filter(EventCreation.brand_name == brand_name).all()
            return [EventRepository._to_dict(event) for event in events]

    @staticmethod
    def update(event_id: int, event_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing event by ID"""
        with get_session() as session:
            event = session.query(EventCreation).filter(EventCreation.id == event_id).first()
            if not event:
                return None

            # Only update fields that are provided
            for field in [
                'brand_name', 'event_name', 'event_address', 'time_in', 'time_out',
                'summary', 'picture', 'price', 'category', 'date',
                'account_name', 'account_number', 'bank',
                'vip_price', 'vvip_price', 'vvvip_price', 'table_price',
            ]:
                if field in event_data and event_data[field] is not None:
                    setattr(event, field, event_data[field])

            session.add(event)
            session.flush()
            session.refresh(event)

            return EventRepository._to_dict(event)

    @staticmethod
    def delete(event_id: int) -> bool:
        """Delete event"""
        with get_session() as session:
            event = session.query(EventCreation).filter(EventCreation.id == event_id).first()
            if not event:
                return False

            session.delete(event)
            return True

    @staticmethod
    def _to_dict(event: EventCreation) -> Dict[str, Any]:
        return {
            "id": event.id,
            "creator_id": event.creator_id,
            "brand_name": event.brand_name,
            "event_name": event.event_name,
            "event_address": event.event_address,
            "time_in": event.time_in,
            "time_out": event.time_out,
            "summary": event.summary,
            "picture": event.picture,
            "price": event.price,
            "category": event.category,
            "date": event.date,
            "account_name": event.account_name,
            "account_number": event.account_number,
            "bank": event.bank,
            "vip_price": event.vip_price,
            "vvip_price": event.vvip_price,
            "vvvip_price": event.vvvip_price,
            "table_price": event.table_price,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
            "is_active": event.is_active,
        }

class TicketRepository:
    """Ticket/User Events data access layer"""

    @staticmethod
    def create(ticket_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new ticket"""
        with get_session() as session:
            ticket = UserEvent(
                user_id=ticket_data.get('user_id'),
                event_id=ticket_data.get('event_id'),
                email=ticket_data.get('email'),
                qrcode_url=ticket_data.get('qrcode_url'),
                token=ticket_data.get('token'),
                ticket_type=ticket_data.get('ticket_type'),
            )
            session.add(ticket)
            session.flush()
            session.refresh(ticket)

            return TicketRepository._to_dict(ticket)

    @staticmethod
    def get_by_id(ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID"""
        with get_session() as session:
            ticket = session.query(UserEvent).filter(UserEvent.id == ticket_id).first()
            return TicketRepository._to_dict(ticket) if ticket else None

    @staticmethod
    def get_by_token(token: str) -> Optional[Dict]:
        """Get ticket by token"""
        import logging
        token = token.strip() if token else ""
        logging.info(f"Looking up ticket with token: '{token}'")
        with get_session() as session:
            ticket = session.query(UserEvent).filter(UserEvent.token == token).first()
            if ticket:
                logging.info(f"Ticket found for token: {token}")
            else:
                logging.warning(f"No ticket found for token: {token}")
            return TicketRepository._to_dict(ticket) if ticket else None

    @staticmethod
    def get_by_user(user_id: int) -> List[Dict]:
        """Get all tickets by user"""
        with get_session() as session:
            tickets = session.query(UserEvent).filter(UserEvent.user_id == user_id).all()
            return [TicketRepository._to_dict(ticket) for ticket in tickets]

    @staticmethod
    def get_by_event(event_id: int) -> List[Dict]:
        """Get all tickets for an event"""
        with get_session() as session:
            tickets = session.query(UserEvent).filter(UserEvent.event_id == event_id).all()
            return [TicketRepository._to_dict(ticket) for ticket in tickets]

    @staticmethod
    def verify(ticket_id: int) -> Optional[Dict]:
        """Mark ticket as verified"""
        from datetime import datetime
        with get_session() as session:
            ticket = session.query(UserEvent).filter(UserEvent.id == ticket_id).first()
            if ticket:
                ticket.isVerified = True
                ticket.verified_at = datetime.now()
                session.commit()
            return TicketRepository._to_dict(ticket) if ticket else None
    @staticmethod
    def delete_by_token(token: str) -> bool:
        """Delete ticket by token"""
        with get_session() as session:
            ticket = session.query(UserEvent).filter(UserEvent.token == token).first()
            if not ticket:
                return False

            session.delete(ticket)
            return True

    @staticmethod
    def delete(ticket_id: int) -> bool:
        """Delete ticket"""
        with get_session() as session:
            ticket = session.query(UserEvent).filter(UserEvent.id == ticket_id).first()
            if not ticket:
                return False

            session.delete(ticket)
            return True

    @staticmethod
    def _to_dict(ticket: UserEvent) -> Dict[str, Any]:
        return {
            "id": ticket.id,
            "user_id": ticket.user_id,
            "event_id": ticket.event_id,
            "attended_at": ticket.attended_at,
            "email": ticket.email,
            "qrcode_url": ticket.qrcode_url,
            "token": ticket.token,
            "ticket_type": ticket.ticket_type,
            "isVerified": ticket.isVerified,
            "verified_at": ticket.verified_at,
            "created_at": ticket.created_at,
        }

class UserInterestsRepository:
    """User Interests data access layer"""

    @staticmethod
    def create(user_id: int, interests: List[str]) -> Optional[Dict]:
        """Create user interests"""
        with get_session() as session:
            record = UserInterest(
                user_id=user_id,
                interests=interests,
            )
            session.add(record)
            session.flush()
            session.refresh(record)

            return UserInterestsRepository._to_dict(record)

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Dict]:
        """Get user interests by user ID"""
        with get_session() as session:
            record = session.query(UserInterest).filter(UserInterest.user_id == user_id).first()
            return UserInterestsRepository._to_dict(record) if record else None

    @staticmethod
    def exists(user_id: int) -> bool:
        """Check if user interests exist"""
        with get_session() as session:
            exists = session.query(UserInterest).filter(UserInterest.user_id == user_id).first() is not None
            return exists

    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete user interests"""
        with get_session() as session:
            record = session.query(UserInterest).filter(UserInterest.user_id == user_id).first()
            if not record:
                return False

            session.delete(record)
            return True

    @staticmethod
    def _to_dict(record: UserInterest) -> Dict[str, Any]:
        return {
            "id": record.id,
            "user_id": record.user_id,
            "interests": record.interests,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

class InterestRepository:
    """Get available interests"""

    @staticmethod
    def get_all_interests() -> Dict[str, List[str]]:
        """Get all available interests"""
        # This returns a predefined list of interests
        interests = {
            "music": ["Rock", "Pop", "Jazz", "Classical", "Hip-Hop", "Electronic"],
            "sports": ["Football", "Basketball", "Tennis", "Cricket", "Swimming"],
            "entertainment": ["Comedy", "Drama", "Action", "Horror", "Animation"],
            "technology": ["AI", "Web Development", "Mobile Apps", "Cybersecurity"],
            "business": ["Startup", "Finance", "Marketing", "Sales"]
        }
        return interests


class TableCategoryRepository:
    """Table categories data access layer"""

    @staticmethod
    def create_for_event(event_id: int, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple table categories for an event.

        Each table dict is expected to use keys similar to the legacy API:
        - tableName
        - tablePrice
        - tableCapacity
        Optionally:
        - available_tables
        """
        created: List[Dict[str, Any]] = []
        with get_session() as session:
            for table in tables:
                category = TableCategory(
                    event_id=event_id,
                    name=table.get('tableName') or table.get('name'),
                    price=table.get('tablePrice') or table.get('price'),
                    capacity=table.get('tableCapacity') or table.get('capacity'),
                    available_tables=table.get('available_tables') or 0,
                )
                session.add(category)
                session.flush()
                session.refresh(category)
                created.append(TableCategoryRepository._to_dict(category))

        return created

    @staticmethod
    def update_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple table categories.

        Each table dict must include 'id' and may include tableName/tablePrice/tableCapacity.
        """
        updated: List[Dict[str, Any]] = []
        with get_session() as session:
            for table in tables:
                table_id = table.get('id')
                if not table_id:
                    continue

                category = session.query(TableCategory).filter(TableCategory.id == table_id).first()
                if not category:
                    continue

                if table.get('tableName') is not None or table.get('name') is not None:
                    category.name = table.get('tableName') or table.get('name')
                if table.get('tablePrice') is not None or table.get('price') is not None:
                    category.price = table.get('tablePrice') or table.get('price')
                if table.get('tableCapacity') is not None or table.get('capacity') is not None:
                    category.capacity = table.get('tableCapacity') or table.get('capacity')
                if table.get('available_tables') is not None:
                    category.available_tables = table.get('available_tables')

                session.add(category)
                session.flush()
                session.refresh(category)
                updated.append(TableCategoryRepository._to_dict(category))

        return updated

    @staticmethod
    def get_by_event(event_id: int) -> List[Dict[str, Any]]:
        """Get all table categories for a given event"""
        with get_session() as session:
            tables = session.query(TableCategory).filter(TableCategory.event_id == event_id).all()
            return [TableCategoryRepository._to_dict(t) for t in tables]

    @staticmethod
    def _to_dict(category: TableCategory) -> Dict[str, Any]:
        return {
            "id": category.id,
            "event_id": category.event_id,
            "name": category.name,
            "capacity": category.capacity,
            "price": category.price,
            "available_tables": category.available_tables,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }
