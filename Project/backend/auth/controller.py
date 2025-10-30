from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database.core import DbSession
from .models import GoogleAuthRequest, TokenResponse, UserResponse
# from .services import AuthService
from . import services


auth_router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/google")


"""
Authenticate user with google ID token
"""
@auth_router.post("/google", response_model=TokenResponse)
async def google_login(auth_request: GoogleAuthRequest, db: DbSession):
    google_user_info = services.verify_google_token(auth_request.id_token)

    user = services.get_current_user(db, google_user_info)

    access_token = services.create_access_token(
        data = {
            "sub": user.email,
            "user_id": str(user.id)
        }
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    ) 

"""
Get current authenticated user
"""
@auth_router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: DbSession = Depends()):
    user = services.get_current_user(db, token)
    return UserResponse.model_validate(user)