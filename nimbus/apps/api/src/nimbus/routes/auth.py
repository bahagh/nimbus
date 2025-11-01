from fastapi import APIRouter, HTTPException, status, Depends
from nimbus.schemas.auth import LoginRequest, TokenPair
from nimbus.security.jwt import create_access_token, create_refresh_token, require_refresh_jwt
from nimbus.models.user import User
from nimbus.db import get_session
from sqlalchemy import text
import hashlib

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# User registration endpoint
@router.post("/register", summary="Register a new user")
async def register(body: LoginRequest, session=Depends(get_session)):
    import re
    if not body.email or not body.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password required")
    # Basic email format check
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", body.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    # Password complexity: min 8 chars, 1 uppercase, 1 lowercase, 1 digit
    if len(body.password) < 8 or not re.search(r"[A-Z]", body.password) or not re.search(r"[a-z]", body.password) or not re.search(r"[0-9]", body.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters, include uppercase, lowercase, and a digit")
    # Check if user exists
    existing = await session.execute(
        text("SELECT * FROM users WHERE email = :email"), {"email": body.email}
    )
    user_row = existing.first()
    if user_row:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    # Hash password
    import hashlib, logging
    hashed = hashlib.sha256(body.password.encode()).digest()
    try:
        # Use direct SQL for user creation (as in working script)
        result = await session.execute(
            text("INSERT INTO users (email, hashed_password) VALUES (:email, :hashed_password) RETURNING id, email"),
            {"email": body.email, "hashed_password": hashed}
        )
        await session.commit()
        inserted = result.first()
        logging.warning(f"Register: user {body.email} created successfully, inserted={inserted}")
        return {"email": body.email, "status": "created", "db": str(inserted) if inserted else None}
    except Exception as e:
        import traceback
        await session.rollback()
        logging.error(f"Register: failed to create user {body.email}: {e}\n{traceback.format_exc()}")
        return {"error": str(e), "trace": traceback.format_exc()}

@router.post("/login", response_model=TokenPair, summary="Issue access and refresh tokens (demo)")
async def login(body: LoginRequest, session=Depends(get_session)):
    import re, logging
    if not body.email or not body.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password required")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", body.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    # Check user in DB
    try:
        result = await session.execute(
            text("SELECT id, email, hashed_password FROM users WHERE email = :email"), {"email": body.email}
        )
        user_row = result.first()
        if not user_row:
            logging.warning(f"Login failed: user not found for email {body.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        hashed = hashlib.sha256(body.password.encode()).digest()
        db_hashed = user_row.hashed_password if hasattr(user_row, "hashed_password") else user_row[2]
        if isinstance(db_hashed, memoryview):
            db_hashed = db_hashed.tobytes()
        if db_hashed != hashed:
            logging.warning(f"Login failed: incorrect password for email {body.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        logging.info(f"Login success for email {body.email}")
        return TokenPair(
            access_token=create_access_token(sub=body.email),
            refresh_token=create_refresh_token(sub=body.email),
        )
    except Exception as e:
        logging.error(f"Login error for email {body.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed due to server error")

@router.post("/refresh", response_model=TokenPair, summary="Exchange refresh token for new tokens")
async def refresh(_claims=Depends(require_refresh_jwt)):
    sub = _claims["sub"]
    return TokenPair(
        access_token=create_access_token(sub=sub),
        refresh_token=create_refresh_token(sub=sub),
    )

@router.post("/debug-db-write", summary="Debug DB write access")
async def debug_db_write(session=Depends(get_session)):
    import hashlib, logging
    from sqlalchemy import text
    email = "debugtest@example.com"
    password = "debugpass123"
    hashed = hashlib.sha256(password.encode()).digest()
    try:
        result = await session.execute(
            text("INSERT INTO users (username, email, hashed_password) VALUES (:username, :email, :hashed_password) RETURNING id, email"),
            {"username": email, "email": email, "hashed_password": hashed}
        )
        await session.commit()
        inserted = result.first()
        logging.warning(f"Debug DB Write: user {email} created, inserted={inserted}")
        return {"email": email, "status": "created", "db": str(inserted) if inserted else None}
    except Exception as e:
        import traceback
        await session.rollback()
        logging.error(f"Debug DB Write: failed to create user {email}: {e}\n{traceback.format_exc()}")
        return {"error": str(e), "trace": traceback.format_exc()}
