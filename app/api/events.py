from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form, BackgroundTasks
from typing import List, Dict, Any, Optional
from app.schema import Event, EventCreate
from app.service.services import event_service, ticket_service
from app.dependencies import get_current_user, optional_current_user
from app.service.email_service import file_service, email_service, cache_service, EmailService
from app.core.security import jwt_service
from datetime import datetime
import json

router = APIRouter(tags=["events"])

@router.post("/event", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_event(
    brand_name: str = Form(...),
    event_name: str = Form(...),
    event_address: str = Form(...),
    time_in: str = Form(...),
    time_out: str = Form(...),
    summary: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    account_name: str = Form(None),  # Optional for free events
    account_number: str = Form(None),  # Optional for free events
    bank: str = Form(None),  # Optional for free events
    vip_price: float = Form(None),
    vvip_price: float = Form(None),
    vvvip_price: float = Form(None),
    table_price: float = Form(None),
    file: UploadFile = File(None),
    current_user: Optional[Dict] = Depends(optional_current_user)
):
    """Create a new event"""
    try:
        # Validate payment details for paid events
        if price and price > 0:
            if not account_name or not account_number or not bank:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment details (account_name, account_number, bank) are required for paid events"
                )

        # Save file if provided
        picture_path = None
        if file:
            try:
                picture_path = file_service.save_upload_file(file)
            except Exception as file_error:
                import logging
                logging.error(f"File upload error: {str(file_error)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image upload failed: {str(file_error)}"
                )

        def parse_time(time_str):
            if not time_str:
                return None
            try:
                # We need to explicitly access datetime from the standard library since we did `from datetime import datetime` at the top of file
                return datetime.strptime(str(time_str), "%H:%M").time()
            except ValueError:
                # Fallback if time format is different
                try:
                    return datetime.strptime(str(time_str), "%H:%M:%S").time()
                except ValueError:
                    return None

        def parse_date(date_str):
            if not date_str:
                return None
            try:
                # Expected format from typical HTML5 date input: YYYY-MM-DD
                return datetime.strptime(str(date_str), "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.strptime(str(date_str), "%d/%m/%Y").date()
                except ValueError:
                    return None

        event_data = {
            "brand_name": brand_name,
            "event_name": event_name,
            "event_address": event_address,
            "time_in": parse_time(time_in),
            "time_out": parse_time(time_out),
            "summary": summary,
            "picture": picture_path,
            "price": price,
            "category": category,
            "date": parse_date(date),
            "account_name": account_name,
            "account_number": account_number,
            "bank": bank,
            "vip_price": vip_price,
            "vvip_price": vvip_price,
            "vvvip_price": vvvip_price,
            "table_price": table_price
        }

        event = event_service.create_event(event_data)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create event"
            )

        return {
            "message": "Event created successfully",
            "userInfo": event
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/updateEvent", response_model=Dict[str, Any])
async def update_event(
    event_id: int = Form(...),
    brand_name: str = Form(None),
    event_name: str = Form(None),
    event_address: str = Form(None),
    time_in: str = Form(None),
    time_out: str = Form(None),
    summary: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    date: str = Form(None),
    account_name: str = Form(None),
    account_number: str = Form(None),
    bank: str = Form(None),
    vip_price: float = Form(None),
    vvip_price: float = Form(None),
    vvvip_price: float = Form(None),
    table_price: float = Form(None),
    file: UploadFile = File(None),
    current_user: Dict = Depends(get_current_user),
):
    """Update an existing event"""
    try:
        picture_path = None
        if file:
            picture_path = file_service.save_upload_file(file)

        def parse_time(time_str):
            if not time_str or isinstance(time_str, datetime):
                return time_str
            try:
                # the file imports datetime at the top `from datetime import datetime`
                return datetime.strptime(str(time_str), "%H:%M").time()
            except ValueError:
                # Fallback if time format is different
                try:
                    return datetime.strptime(str(time_str), "%H:%M:%S").time()
                except ValueError:
                    return None

        def parse_date(date_str):
            if not date_str or isinstance(date_str, datetime):
                return date_str
            try:
                # Expected format from typical HTML5 date input: YYYY-MM-DD
                return datetime.strptime(str(date_str), "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.strptime(str(date_str), "%d/%m/%Y").date()
                except ValueError:
                    return None

        event_data: Dict[str, Any] = {
            "brand_name": brand_name,
            "event_name": event_name,
            "event_address": event_address,
            "time_in": parse_time(time_in),
            "time_out": parse_time(time_out),
            "summary": summary,
            "picture": picture_path,
            "price": price,
            "category": category,
            "date": parse_date(date),
            "account_name": account_name,
            "account_number": account_number,
            "bank": bank,
            "vip_price": vip_price,
            "vvip_price": vvip_price,
            "vvvip_price": vvvip_price,
            "table_price": table_price,
        }

        updated = event_service.update_event(event_id, event_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found or update failed",
            )

        return {"message": "Event updated successfully", "updatedEvent": updated}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.get("/getEvent", response_model=Dict[str, Any])
async def get_event(eventId: int = None):
    """Get event by ID"""
    if not eventId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event ID is required"
        )

    event = event_service.get_event(eventId)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return {"event": [event]}

@router.get("/getAllEvent", response_model=Dict[str, Any])
async def get_all_events():
    """Get all events"""
    events = event_service.get_all_events()

    if not events:
        return {"event": []}

    return {"event": events}


@router.get("/getEventCreated", response_model=List[Dict[str, Any]])
async def get_event_created(brand: str):
    """Get events created by a specific brand/creator"""
    events = event_service.get_events_by_brand(brand)
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has not created any event",
        )
    return events

@router.get("/getEventByCategory/{category}", response_model=List[Dict[str, Any]])
async def get_events_by_category(category: str):
    """Get events by category"""
    return event_service.get_events_by_category(category)


@router.get("/eventCategory", response_model=Dict[str, Any])
async def get_events_by_category_query(category: str):
    """Get events by category (query param variant for legacy compatibility)"""
    events = event_service.get_events_by_category(category)
    return {"event": events}


@router.post("/tableCreation", response_model=Dict[str, Any])
async def table_creation(payload: Dict[str, Any]):
    """Create table categories for an event.

    Expects JSON body with:
    - event_id: int
    - tables: list[{tableName, tablePrice, tableCapacity, available_tables?}]
    """
    event_id = payload.get("event_id")
    tables = payload.get("tables", [])

    if not event_id or not isinstance(tables, list) or not tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_id and tables are required",
        )

    created = event_service.create_table_categories(event_id, tables)
    return {
        "message": f"{len(created)} table(s) created",
        "tableInfo": created,
    }


@router.put("/updateTableCreation", response_model=Dict[str, Any])
async def update_table_creation(payload: Dict[str, Any]):
    """Update existing table categories.

    Expects JSON body with:
    - tables: list[{id, tableName, tablePrice, tableCapacity, available_tables?}]
    """
    tables = payload.get("tables", [])

    if not isinstance(tables, list) or not tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tables list is required",
        )

    updated = event_service.update_table_categories(tables)
    return {
        "message": f"{len(updated)} table(s) updated successfully",
        "updatedTables": updated,
    }

@router.post("/attendEvent", response_model=Dict[str, Any])
async def attend_event(
    event_id: int = Form(...),
    email: str = Form(...),
    ticket_type: str = Form(...),
    token: str = Form(...),  # Token from frontend, not generated
    qrcode_url: str = Form(None),
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):
    """Attend an event (purchase ticket)"""
    event = event_service.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Use the token from frontend, don't generate a new one
    if not token or len(token.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )

    ticket_data = {
        "event_id": event_id,
        "user_id": current_user["id"],
        "email": email,
        "qrcode_url": qrcode_url,
        "token": token,
        "ticket_type": ticket_type
    }

    ticket = ticket_service.create_ticket(ticket_data)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create ticket"
        )

    # Send confirmation email
    username = current_user.get('username', 'User')
    event_name = event.get('event_name', 'Event')
    event_pic = event.get('picture', '')
    event_date = event.get('date', '')
    event_category = event.get('category', '')

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Event Payment Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
            h1 {{ color: #4CAF50; }}
            img {{ width: 300px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <p>Hello {username},</p>
        <p>You have successfully paid for the event: <strong>{event_name}</strong>.</p>
        <div>
            <img src="{event_pic if str(event_pic).startswith('http') else f'https://app.samdavweb.org.ng/{event_pic}'}" alt="{event_name} Picture" style="width: 300px;"/>
        </div>
        <ul>
            <li>Your Token for the event: {token}</li>
            <li>Your QR code for the event: <a href="{qrcode_url}" style="color: #1a73e8;">{qrcode_url}</a></li>
        </ul>
        <div>
            Thanks for choosing Owl event website.
            <h1>Enjoy your event!</h1>
        </div>
    </body>
    </html>
    """

    # Build branded payment success email from template
    event_image_url = event_pic if str(event_pic).startswith('http') else f"https://app.samdavweb.org.ng/{event_pic}"
    html_body = EmailService.render_template(
        "payment_success.html",
        {
            "username": username,
            "event_name": event_name,
            "event_date": event_date,
            "category": event_category,
            "token": token,
            "qrcode_url": qrcode_url,
            "event_image_url": event_image_url,
        },
    )

    # Send confirmation email in background to avoid blocking
    if background_tasks is not None:
        background_tasks.add_task(
            email_service._send_sync,
            email,
            "THE OWL INITIATORS: Payment Successful",
            html_body,
            True,
        )
    else:
        # Fallback for cases where BackgroundTasks isn't provided
        await email_service.send_email(
            email,
            "THE OWL INITIATORS: Payment Successful",
            html_body,
        )

    return {
        "message": "Event attended successfully",
        "ticket": ticket
    }

@router.get("/getAttendedEvents", response_model=Dict[str, Any])
async def get_attended_events(current_user: Dict = Depends(get_current_user)):
    """Get all events attended by current user"""
    tickets = ticket_service.get_user_tickets(current_user["id"])

    return {"event": tickets}

@router.get("/getAttendee", response_model=List[Dict[str, Any]])
async def get_attendees(eventId: int = None):
    """Get all attendees for an event"""
    if not eventId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event ID is required"
        )

    return ticket_service.get_event_attendees(eventId)

@router.delete("/deleteEvent")
async def delete_event(
    event_id: int = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Delete an event"""
    success = event_service.delete_event(event_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return {"message": "Event Deleted Successfully"}

@router.delete("/deleteTicket")
async def delete_ticket(
    token: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Delete a ticket by token"""
    success = ticket_service.delete_ticket_by_token(token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or invalid token"
        )

    return {"message": "Token deleted successfully"}

@router.post("/verifyToken", response_model=Dict[str, Any])
async def verify_token(token: str = Form(...)):
    """Verify event token"""
    import logging
    logging.info(f"Received token for verification: '{token}'")

    ticket = ticket_service.get_ticket_by_token(token)

    if not ticket:
        logging.error(f"Ticket not found for token: {token}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token"
        )

    # Check if already verified
    if ticket.get('isVerified'):
        logging.warning(f"Token already verified: {token}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This ticket has already been verified and used"
        )

    # Mark ticket as verified
    ticket_id = ticket.get('id')
    updated_ticket = ticket_service.verify_ticket(ticket_id)
    logging.info(f"Ticket {ticket_id} marked as verified")

    user_id = ticket.get('user_id')
    event_id = ticket.get('event_id')

    logging.info(f"Ticket details - user_id: {user_id}, event_id: {event_id}")

    # Get user details
    from app.repo.repositories import UserProfileRepository, CreatorProfileRepository
    user_profile = UserProfileRepository.get_by_user_id(user_id)
    if not user_profile:
        logging.info(f"UserProfile not found for user_id {user_id}, trying CreatorProfile")
        user_profile = CreatorProfileRepository.get_by_user_id(user_id)

    logging.info(f"User profile: {user_profile}")

    # Get event details
    event = event_service.get_event(event_id)
    logging.info(f"Event: {event}")

    if not event:
        logging.error(f"Event not found for event_id: {event_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # User profile is optional - they may not have created one yet
    if not user_profile:
        logging.warning(f"User profile not found for user_id {user_id}, returning ticket without profile")

    return {
        "message": "Token verified successfully",
        "ticket": updated_ticket,
        "user": user_profile,  # Can be None if user hasn't created profile yet
        "event": event
    }


@router.get("/getDashboard", response_model=Dict[str, Any])
async def get_dashboard(brand: str):
    """Get dashboard statistics for a brand's events"""
    dashboard = event_service.get_dashboard(brand)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No events found for this brand",
        )
    return dashboard
