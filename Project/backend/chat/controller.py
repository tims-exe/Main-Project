from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

import uuid
from ..middleware.auth_middleware import auth_middleware
from ..auth.models import TokenData
from ..data.redis_client import redis_client
from .models import ChatRequest
from .services import save_and_convert_audio

chat_router = APIRouter(
    prefix='/chat',
    tags=["Chat"]
)


@chat_router.post("/text")
async def text(req: ChatRequest, payload: TokenData = Depends(auth_middleware)):
    request_id = str(uuid.uuid4())

    try:
        job_message = {
            "user_id": payload.user_id,
            "type": "text",
            "message": req.message
        }

        await redis_client.send_to_engine(
            request_id=request_id,
            data=job_message
        )

        ack_response = await redis_client.wait_for_response(request_id)

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
    

@chat_router.post("/voice")
async def voice(audio: UploadFile = File(...), payload: TokenData = Depends(auth_middleware)):
    request_id = str(uuid.uuid4())

    try:
        print("audio received")

        # save and convert the audio file from request
        mp3_path = save_and_convert_audio(
            audio=audio,
            user_id=payload.user_id,
            request_id=request_id
        )

        print('AUDIO PATH = ', mp3_path)

        # job request
        job_message = {
            "user_id": payload.user_id,
            "type": "audio",
            "message": str(mp3_path)
        }

        print("JOB : ", job_message)

        # send job 
        await redis_client.send_to_engine(
            request_id=request_id,
            data=job_message
        )

        print("JOB REQ SENT")

        ack_response = await redis_client.wait_for_response(request_id)

        print("JOB REQ RECIEVED", ack_response)

        return {
            "message": ack_response.get("message"),
            "request_id": request_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )


        # create job msg with audio id

        # send msg to queue

        # recieve ack text

        # return response


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