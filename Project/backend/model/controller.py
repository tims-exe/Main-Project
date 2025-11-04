from fastapi import APIRouter, Depends
from ..middleware.auth_middleware import auth_middleware

model_router = APIRouter(
    prefix='/model',
    tags=["Model"]
)

@model_router.get("/test")
async def testing(payload: dict = Depends(auth_middleware)):
    return {"message": "Access granted", "user": payload}