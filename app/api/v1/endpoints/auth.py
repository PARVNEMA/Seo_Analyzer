from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.supabase import supabase
from app.schemas.auth import UserCredentials, TokenResponse

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(credentials: UserCredentials):
    """Register a new user with Supabase."""
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
        })

        if not response.session:
            # Depending on Supabase settings, sign_up might require email confirmation
            # and session will be None.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration successful but email confirmation might be required."
            )

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserCredentials):
    """Authenticate with Supabase and get a session token."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed."
            )

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or authentication error."
        )

@router.post("/logout")
async def logout():
    """Sign out the current user session."""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
