from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

from ..entities.user import User
from .models import TokenData


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# verify google ID token and return user info
def verify_google_token(token: str) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        if id_info['aud'] != GOOGLE_CLIENT_ID:
            raise ValueError("Could not verify")
        
        return id_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )


# get existing user or create new one
def get_user(db: Session, google_user_info: dict) -> User:
    email = google_user_info.get('email')
    google_id = google_user_info.get('sub')

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
        email = email,
        google_id = google_id,
        first_name = google_user_info.get('given_name'),
        last_name = google_user_info.get("family_name"),
        profile_picture = google_user_info.get('picture')
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