from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

# class VoiceRequest(BaseModel):
