from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database.core import DbSession
from .models import TokenResponse, UserResponse
from . import services
import os
import json
from urllib.parse import quote

auth_router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/google")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

"""
Initiate Google OAuth flow
"""
@auth_router.get("/google/login")
async def google_login():
    auth_url = services.get_google_auth_url()
    return {"auth_url": auth_url}

"""
Google OAuth callback - exchanges code for tokens
"""
@auth_router.get("/google/callback")
async def google_callback(code: str, db: DbSession):
    try:
        google_user_info = services.exchange_code_for_token(code)
        user = services.get_user(db, google_user_info)
        
        access_token = services.create_access_token(
            data={
                "sub": user.email,
                "user_id": str(user.id)
            }
        )
        
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": user.profile_picture
        }
        user_json = quote(json.dumps(user_data))

        print(f"TOKEN : {access_token}")
        
        redirect_url = f"{FRONTEND_URL}/auth/callback?token={access_token}&user={user_json}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        error_url = f"{FRONTEND_URL}/login?error={str(e)}"
        return RedirectResponse(url=error_url)

"""
Get current authenticated user
"""
@auth_router.get("/me", response_model=UserResponse)
async def get_current_user(db: DbSession, token: str = Depends(oauth2_scheme)):
    user = services.get_current_user(db, token)
    return UserResponse.model_validate(user)