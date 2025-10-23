import torch
import torch.nn as nn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torchaudio
import numpy as np
import snntorch.spikegen as spikegen
import io

# ------------------------------
# Import your model class
# ------------------------------
from model import SpikeAttentionNet  # <- make sure this file exists

# ------------------------------
# FastAPI setup
# ------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def health():
    return {"message": "Server Running"}

# ------------------------------
# Load model once on startup
# ------------------------------
MODEL_PATH = "best_model.pth"
IN_DIM = 1611        # same as training
NUM_CLASSES = 7
EMBED_DIM = 256
NUM_HEADS = 4
T = 25

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = SpikeAttentionNet(
    in_dim=IN_DIM,
    embed_dim=EMBED_DIM,
    num_heads=NUM_HEADS,
    num_classes=NUM_CLASSES
).to(device)

state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)
model.eval()

# Optional label mapping
label_map = {
    0: "Neutral",
    1: "Happy",
    2: "Sad",
    3: "Angry",
    4: "Fearful",
    5: "Disgust",
    6: "Surprised",
}


# ------------------------------
# Utility: audio → features → spikes
# ------------------------------
def preprocess_audio_to_spikes(audio_bytes, T=25):
    waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
    waveform = waveform.mean(dim=0, keepdim=True)

    mel_spec = torchaudio.transforms.MelSpectrogram(
        sample_rate=sample_rate,
        n_fft=1024,
        hop_length=512,
        n_mels=128
    )(waveform)

    mel_spec = torchaudio.transforms.AmplitudeToDB()(mel_spec)
    mel_spec = mel_spec.squeeze(0).T  # [time, 128]

    # Average pool or pad to match expected dimension 1611
    feat = mel_spec.mean(dim=0).numpy()  # [128]
    feat = np.pad(feat, (0, 1611 - len(feat)))  # pad up to 1611

    feat = feat.astype(np.float32)
    feat = feat / (np.linalg.norm(feat) + 1e-6)
    feat = np.clip(feat, 0, 1.0)

    S = spikegen.rate(torch.tensor(feat), num_steps=T).float()  # [T, F=1611]
    mask = torch.ones(T, dtype=torch.bool)
    return S.unsqueeze(0), mask.unsqueeze(0)




# ------------------------------
# API Routes
# ------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    print(f"Received message: {request.message}")
    return ChatResponse(response="Ok")


@app.post("/api/voice", response_model=ChatResponse)
async def voice(audio: UploadFile = File(...)):
    print(f"Received audio file: {audio.filename}")
    audio_bytes = await audio.read()

    try:
        spikes, mask = preprocess_audio_to_spikes(audio_bytes, T=T)
        spikes, mask = spikes.to(device), mask.to(device)

        with torch.no_grad():
            logits = model(spikes, mask=mask)
            pred = logits.argmax(dim=1).item()

        label = label_map.get(pred, f"Class {pred}")
        print(f"Predicted emotion: {label}")

        return ChatResponse(response=f"Model predicts: {label}")

    except Exception as e:
        print(f"Error during inference: {e}")
        return ChatResponse(response="Error processing audio")


# ------------------------------
# Run command
# ------------------------------
# uvicorn main:app --reload
