from app.repo.repositories import (
    UserRepository, CreatorProfileRepository, UserProfileRepository,
    EventRepository, TicketRepository, UserInterestsRepository, InterestRepository,
    TableCategoryRepository,
)
from app.core.security import jwt_service
from typing import Dict, Any, Optional, List

class UserService:
    """Business logic for users"""

    @staticmethod
    def register_user(username: str, email: str, password_hash: str) -> Optional[Dict]:
        """Register a new user (password_hash must already be hashed)."""
        # Check if user already exists
        existing = UserRepository.get_by_email(email)
        if existing:
            return None

        user = UserRepository.create(username, email, password_hash)
        return user

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict]:
        """Authenticate a user"""
        user = UserRepository.get_by_email(email)
        if not user:
            return None

        if not jwt_service.verify_password(password, user.get('password', '')):
            return None

        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        return UserRepository.get_by_email(email)

    @staticmethod
    def reset_password(email: str, new_password: str) -> bool:
        """Reset user password"""
        user = UserRepository.get_by_email(email)
        if not user:
            return False

        password_hash = jwt_service.hash_password(new_password)
        return UserRepository.update_password(email, password_hash)

class ProfileService:
    """Business logic for user profiles"""

    @staticmethod
    def create_creator_profile(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a creator profile"""
        # Check if profile already exists
        if CreatorProfileRepository.exists(profile_data.get('user_id'), profile_data.get('email')):
            return None

        return CreatorProfileRepository.create(profile_data)

    @staticmethod
    def create_user_profile(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a user profile"""
        # Check if profile already exists
        if UserProfileRepository.exists(profile_data.get('user_id'), profile_data.get('email')):
            return None

        return UserProfileRepository.create(profile_data)

    @staticmethod
    def get_profile(user_id: int) -> Optional[Dict]:
        """Get user profile (checks both creator and user profiles)"""
        creator_profile = CreatorProfileRepository.get_by_user_id(user_id)
        if creator_profile:
            return creator_profile

        return UserProfileRepository.get_by_user_id(user_id)

    @staticmethod
    def update_creator_profile(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Update a creator profile"""
        user_id = profile_data.get('user_id')
        if not user_id:
            return None
        return CreatorProfileRepository.update(user_id, profile_data)

    @staticmethod
    def update_user_profile(profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Update a user profile"""
        user_id = profile_data.get('user_id')
        if not user_id:
            return None
        return UserProfileRepository.update(user_id, profile_data)

class EventService:
    """Business logic for events"""

    @staticmethod
    def create_event(event_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new event"""
        return EventRepository.create(event_data)

    @staticmethod
    def get_event(event_id: int) -> Optional[Dict]:
        """Get event by ID"""
        return EventRepository.get_by_id(event_id)

    @staticmethod
    def get_all_events() -> List[Dict]:
        """Get all events"""
        return EventRepository.get_all()

    @staticmethod
    def get_events_by_category(category: str) -> List[Dict]:
        """Get events by category"""
        return EventRepository.get_by_category(category)

    @staticmethod
    def delete_event(event_id: int) -> bool:
        """Delete an event"""
        return EventRepository.delete(event_id)

    @staticmethod
    def update_event(event_id: int, event_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing event"""
        return EventRepository.update(event_id, event_data)

    @staticmethod
    def get_events_by_brand(brand_name: str) -> List[Dict]:
        """Get events created by a specific brand/creator"""
        return EventRepository.get_by_brand(brand_name)

    @staticmethod
    def create_table_categories(event_id: int, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create table categories for an event"""
        return TableCategoryRepository.create_for_event(event_id, tables)

    @staticmethod
    def update_table_categories(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple table categories"""
        return TableCategoryRepository.update_tables(tables)

    @staticmethod
    def get_dashboard(brand_name: str) -> Optional[Dict[str, Any]]:
        """Get simple dashboard statistics for a brand's events"""
        events = EventRepository.get_by_brand(brand_name)
        if not events:
            return None

        total_tickets = 0
        total_revenue = 0.0
        event_details: List[Dict[str, Any]] = []

        for event in events:
            event_id = event.get("id")
            tickets = TicketRepository.get_by_event(event_id)
            attendees = len(tickets)

            revenue = 0.0
            for ticket in tickets:
                ticket_type = (ticket.get("ticket_type") or "").upper()
                price = event.get("price") or 0.0
                if ticket_type == "VIP" and event.get("vip_price") is not None:
                    price = event.get("vip_price") or price
                elif ticket_type == "VVIP" and event.get("vvip_price") is not None:
                    price = event.get("vvip_price") or price
                elif ticket_type.startswith("VVV") and event.get("vvvip_price") is not None:
                    price = event.get("vvvip_price") or price

                try:
                    revenue += float(price or 0.0)
                except (TypeError, ValueError):
                    continue

            total_tickets += attendees
            total_revenue += revenue

            event_details.append(
                {
                    "id": event.get("id"),
                    "event_name": event.get("event_name"),
                    "date": event.get("date"),
                    "category": event.get("category"),
                    "picture": event.get("picture"),
                    "price": event.get("price"),
                    "attendees": attendees,
                    "revenue": revenue,
                }
            )

        return {
            "brand": brand_name,
            "totalEvents": len(events),
            "totalTickets": total_tickets,
            "totalRevenue": total_revenue,
            "events": event_details,
        }

class TicketService:
    """Business logic for tickets"""

    @staticmethod
    def create_ticket(ticket_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new ticket"""
        return TicketRepository.create(ticket_data)

    @staticmethod
    def get_ticket(ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID"""
        return TicketRepository.get_by_id(ticket_id)

    @staticmethod
    def get_ticket_by_token(token: str) -> Optional[Dict]:
        """Get ticket by token"""
        return TicketRepository.get_by_token(token)

    @staticmethod
    def verify_ticket(ticket_id: int) -> Optional[Dict]:
        """Mark ticket as verified"""
        return TicketRepository.verify(ticket_id)

    @staticmethod
    def get_user_tickets(user_id: int) -> List[Dict]:
        """Get all tickets for a user"""
        return TicketRepository.get_by_user(user_id)

    @staticmethod
    def get_event_attendees(event_id: int) -> List[Dict]:
        """Get all attendees for an event"""
        return TicketRepository.get_by_event(event_id)

    @staticmethod
    def delete_ticket_by_token(token: str) -> bool:
        """Delete a ticket by token"""
        return TicketRepository.delete_by_token(token)

    @staticmethod
    def delete_ticket(ticket_id: int) -> bool:
        """Delete a ticket"""
        return TicketRepository.delete(ticket_id)

class InterestService:
    """Business logic for user interests"""

    @staticmethod
    def get_all_interests() -> Dict[str, List[str]]:
        """Get all available interests"""
        return InterestRepository.get_all_interests()

    @staticmethod
    def add_user_interests(user_id: int, interests: List[str]) -> Optional[Dict]:
        """Add interests for a user"""
        # Check if user already has interests
        if UserInterestsRepository.exists(user_id):
            return None

        return UserInterestsRepository.create(user_id, interests)

    @staticmethod
    def get_user_interests(user_id: int) -> Optional[Dict]:
        """Get user interests"""
        return UserInterestsRepository.get_by_user_id(user_id)

    @staticmethod
    def get_interested_events(user_id: int) -> List[Dict]:
        """Get events based on user interests"""
        user_interests = UserInterestsRepository.get_by_user_id(user_id)
        if not user_interests:
            return []

        # interests is already a list from ORM
        interests = user_interests.get('interests') or []

        # Get all events
        all_events = EventRepository.get_all()

        # Filter events by matching category with interests
        interested_events = [
            event for event in all_events
            if event.get('category') in interests
        ]

        return interested_events

user_service = UserService()
profile_service = ProfileService()
event_service = EventService()
ticket_service = TicketService()
interest_service = InterestService()
