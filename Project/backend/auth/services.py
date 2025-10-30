from sqlalchemy.orm import Session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import os
import requests
from urllib.parse import urlencode

from ..entities.user import User
from .models import TokenData

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

REDIRECT_URI = f"{BACKEND_URL}/auth/google/callback"

# Generate Google OAuth URL
def get_google_auth_url() -> str:
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return auth_url

# Exchange authorization code for tokens and get user info
def exchange_code_for_token(code: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        # Get user info using access token
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        
        return userinfo_response.json()
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to exchange code for token: {str(e)}"
        )

# get existing user or create new one
def get_user(db: Session, google_user_info: dict) -> User:
    email = google_user_info.get('email')
    google_id = google_user_info.get('id')

    user = db.query(User).filter(
        (User.email == email) | (User.google_id == google_id)
    ).first()

    if user:
        if not user.google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)
        return user 

    user = User(
        email=email,
        google_id=google_id,
        first_name=google_user_info.get('given_name'),
        last_name=google_user_info.get('family_name'),
        profile_picture=google_user_info.get('picture')
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user 

# create jwt access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# verify jwt token
def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return TokenData(email=email)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# get current user from jwt token
def get_current_user(db: Session, token: str) -> User:
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user