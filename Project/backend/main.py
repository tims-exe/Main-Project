import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torchaudio
import numpy as np
import snntorch.spikegen as spikegen
import io
from spikingjelly.activation_based import functional
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import logout
from .api import register_routes
from .data.database import engine, Base
from contextlib import asynccontextmanager
from .data.redis_client import redis_client
# Import your efficient SpikeNet model
# from .model import SpikeNetEfficient as SpikeNet


# ---------------- FASTAPI SETUP ----------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.disconnect()



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base.metadata.create_all(bind=engine)


register_routes(app)



@app.get("/")
async def health():
    return {"message": "Server Running"}




# # 🎙️ Voice input — only emotion prediction
# @app.post("/api/voice", response_model=ChatResponse)
# async def voice(audio: UploadFile = File(...)):
#     audio_bytes = await audio.read()
#     try:
#         emotion, confidence = detect_emotion(audio_bytes)
#         print(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")

#         # Return only emotion prediction, no LLM
#         return ChatResponse(
#             response=f"Detected emotion: {emotion} (confidence: {confidence:.2f})",
#             emotion=emotion
#         )
#     except Exception as e:
#         print(f"Error processing voice input: {e}")
#         return ChatResponse(response="Error processing audio", emotion="Neutral")


# # Run with:
# # pip install fastapi uvicorn torchaudio snntorch transformers huggingface_hub
# # uvicorn main:app --reload