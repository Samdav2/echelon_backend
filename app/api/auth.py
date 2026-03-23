from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.schema import (
    UserCreate, LoginRequest, TokenResponse,
    VerificationCodeRequest, VerifyCodeRequest, ResetPasswordRequest
)
from app.service.services import user_service
from app.service.email_service import email_service, cache_service, EmailService
from app.core.security import jwt_service
from app.repo.repositories import UserRepository

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=dict, status_code=status.HTTP_200_OK)
async def signup(data: UserCreate, background_tasks: BackgroundTasks):
    """Register a new user - Step 1: Request verification code"""
    email = data.email
    username = data.username
    password = data.password

    if not all([email, username, password]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, username, and password are required"
        )

    # Check if user already exists
    existing_user = user_service.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already exists with email {email}"
        )

    # Generate verification code
    code = jwt_service.generate_verification_code()

    # Hash password for storage
    password_hash = jwt_service.hash_password(password)

    # Store in cache temporarily
    cache_service.set(email, {
        'username': username,
        'email': email,
        'password': password_hash,
        'code': code,
        'type': 'signup'
    })

    # Send verification code via email using branded template
    html_body = EmailService.render_template(
        "verification_signup.html",
        {"username": username, "code": code},
    )

    # Send email in background so the request returns quickly
    background_tasks.add_task(
        email_service._send_sync,
        email,
        "Verification Code",
        html_body,
        True,
    )

    return {"message": "A verification code has been sent to your email"}

@router.post("/verify-code", response_model=dict, status_code=status.HTTP_200_OK)
async def verify_code(data: VerifyCodeRequest, background_tasks: BackgroundTasks):
    """Verify code and complete signup"""
    email = data.email
    code = data.code

    # Get cached user data
    cached_data = cache_service.get(email)

    if not cached_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or code expired"
        )

    # Verify code
    if code != cached_data.get('code'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    if cached_data.get('type') == 'signup':
        # Check if user already exists
        existing_user = UserRepository.get_by_username(cached_data.get('username'))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Create user in database
        user = user_service.register_user(
            username=cached_data.get('username'),
            email=cached_data.get('email'),
            password_hash=cached_data.get('password')  # Already hashed
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register user"
            )

        # Generate JWT token
        access_token = jwt_service.create_token(
            data={"user_id": user["id"], "email": user["email"]}
        )

        # Send welcome email
        try:
            welcome_html = EmailService.render_template(
                "welcome_user.html",
                {"username": user.get("username", "there")},
            )
            background_tasks.add_task(
                email_service._send_sync,
                user["email"],
                "Welcome to Ticket Lounge",
                welcome_html,
                True,
            )
        except Exception:
            pass

        # Clear cache
        cache_service.delete(email)

        return {
            "message": "User registered successfully",
            "profile": {
                "user_id": user["id"],
                "username": user["username"],
                "email": user["email"]
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    elif cached_data.get('type') == 'resetpassword':
        # Update password in database
        success = user_service.reset_password(email, cached_data.get('password'))

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Clear cache
        cache_service.delete(email)

        return {"message": "Password successfully updated"}

    else:
        # Default verification success (for send-verification-code)
        # Clear cache
        cache_service.delete(email)

        try:
            success_html = EmailService.render_template(
                "verification_success.html",
                {}
            )
            background_tasks.add_task(
                email_service._send_sync,
                email,
                "Email Verified Successfully",
                success_html,
                True,
            )
        except Exception:
            pass

        return {"message": "Verification successful"}

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Login user and return JWT token"""
    user = user_service.authenticate_user(
        email=credentials.email,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = jwt_service.create_token(
        data={"user_id": user["id"], "email": user["email"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profile": user,
        "user_id": user["id"]
    }

@router.post("/send-verification-code", response_model=dict)
async def send_verification_code(data: VerificationCodeRequest, background_tasks: BackgroundTasks):
    """Send verification code to email"""
    email = data.email
    code = jwt_service.generate_verification_code()

    # Store in cache
    cache_service.set(email, {'code': code})

    # Send email using shared verification template
    html_body = EmailService.render_template(
        "verification_generic.html",
        {"code": code},
    )

    background_tasks.add_task(
        email_service._send_sync,
        email,
        "Verification Code",
        html_body,
        True,
    )

    return {"message": "Verification code sent successfully"}

@router.post("/reset-password", response_model=dict)
async def reset_password(data: dict, background_tasks: BackgroundTasks):
    """Request password reset - Step 1"""
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and new password are required"
        )

    # Check if user exists
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate verification code
    code = jwt_service.generate_verification_code()

    # Hash new password
    password_hash = jwt_service.hash_password(new_password)

    # Store in cache temporarily
    cache_service.set(email, {
        'password': password_hash,
        'code': code,
        'type': 'resetpassword'
    })

    # Send verification code using reset-password template
    html_body = EmailService.render_template(
        "reset_password_code.html",
        {"code": code},
    )

    background_tasks.add_task(
        email_service._send_sync,
        email,
        "Password Reset Code",
        html_body,
        True,
    )

    return {"message": "A verification code has been sent to your email"}
