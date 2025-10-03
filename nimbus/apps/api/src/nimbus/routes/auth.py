from fastapi import APIRouter, HTTPException, status, Depends
from nimbus.schemas.auth import LoginRequest, TokenPair
from nimbus.security.jwt import create_access_token, create_refresh_token, require_refresh_jwt

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/login", response_model=TokenPair, summary="Issue access and refresh tokens (demo)")
async def login(body: LoginRequest):
    # TODO: validate user in DB; demo accepts any non-empty
    if not body.username or not body.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    return TokenPair(
        access_token=create_access_token(sub=body.username),
        refresh_token=create_refresh_token(sub=body.username),
    )

@router.post("/refresh", response_model=TokenPair, summary="Exchange refresh token for new tokens")
async def refresh(_claims=Depends(require_refresh_jwt)):
    sub = _claims["sub"]
    return TokenPair(
        access_token=create_access_token(sub=sub),
        refresh_token=create_refresh_token(sub=sub),
    )
