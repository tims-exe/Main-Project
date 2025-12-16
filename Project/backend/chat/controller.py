from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

import uuid
from ..middleware.auth_middleware import auth_middleware
from ..auth.models import TokenData
from ..data.redis_client import redis_client
from .models import ChatRequest, JobMsgType
from .services import save_and_convert_audio
from pydantic import BaseModel

chat_router = APIRouter(
    prefix='/chat',
    tags=["Chat"]
)


@chat_router.post("/text")
async def text(req: ChatRequest, payload: TokenData = Depends(auth_middleware)):
    request_id = str(uuid.uuid4())

    job_message = JobMsgType(
        user_id=payload.user_id,
        type="text",
        data=req.message
    )

    await redis_client.send_to_engine(request_id, job_message)

    response = await redis_client.wait_for_response(request_id)

    return {
        "message": response.get("message"),
        "request_id": request_id
    }

    

@chat_router.post("/voice")
async def voice(audio: UploadFile = File(...), payload: TokenData = Depends(auth_middleware) ):
    request_id = str(uuid.uuid4())

    mp3_path = save_and_convert_audio(
        audio=audio,
        user_id=payload.user_id,
        request_id=request_id
    )

    job_message = JobMsgType(
        user_id=payload.user_id,
        type="audio",
        data=request_id
    )

    await redis_client.send_to_engine(request_id, job_message)

    response = await redis_client.wait_for_response(request_id)

    print(response)

    return {
        "message": response.get("message"),
        "request_id": request_id
    }



@chat_router.get("/test")
async def testing(payload: TokenData = Depends(auth_middleware)):
    print("/model/test")
    request_id = str(uuid.uuid4())
    
    try:
        # Send data to Redis stream
        await redis_client.send_to_engine(
            request_id=request_id,
            data={"email": payload.email}
        )
        
        # Wait for acknowledgement from engine
        ack_response = await redis_client.wait_for_response(request_id, timeout=5.0)
        
        # Return the acknowledgement message to the user
        return {
            "message": ack_response.get("message"),
            "request_id": request_id
        }
    
    except TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Request Timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )