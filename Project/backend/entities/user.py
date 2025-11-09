from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid 
from ..data.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=False)
    profile_picture = Column(String, nullable=True)