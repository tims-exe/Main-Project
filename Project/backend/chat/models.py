from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

# class VoiceRequest(BaseModel):


class JobMsgType(BaseModel):
    user_id: str
    type: str
    data: str