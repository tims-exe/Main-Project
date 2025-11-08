from fastapi import APIRouter, Depends
import uuid
from ..middleware.auth_middleware import auth_middleware
from ..auth.models import TokenData
from ..data.redis_client import redis_client

model_router = APIRouter(
    prefix='/model',
    tags=["Model"]
)


@model_router.get("/test")
async def testing(payload: TokenData = Depends(auth_middleware)):
    request_id = str(uuid.uuid4())
    
    await redis_client.send_to_engine(
        request_id=request_id,
        data={"email": payload.email}
    )
    
    return {
        "message": "Request sent to engine",
        "request_id": request_id,
        "user": payload.email
    }
