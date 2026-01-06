import torch
import torch.nn.functional as F
import librosa
import numpy as np
import os

from .modules.SpikEmo_Model import SpikEmo
from .modules.spikformer import Spikformer

# ---------------- CONFIG (must match training) ----------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DATASET = "IEMOCAP"
N_CLASSES = 6
N_SPEAKERS = 2

ROBERTA_DIM = 768
D_M_AUDIO = 40
D_M_VISUAL = 512
MODEL_DIM = 256
HIDDEN_DIM = 256
NUM_LAYERS = 6
NUM_HEADS = 8

D_G = 64
D_P = 64
D_E = 64
D_H = 64
D_A = 32

DROPOUT = 0.1
DROPOUT_REC = 0.1

TAU = 10.0
COMMON_THR = 1.0
SPIKE_T = 32

MULTI_ATTN = True
LISTENER_STATE = True
CONTEXT_ATTENTION = True

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINT_PATH = os.path.join(
    CURRENT_DIR,
    "spikemo_best_IEMOCAP.pt"
)

print("Loading checkpoint from:", CHECKPOINT_PATH)
print("Exists:", os.path.exists(CHECKPOINT_PATH))


LABEL_MAP = {
    0: "happiness",
    1: "sadness",
    2: "neutral",
    3: "anger",
    4: "excitement",
    5: "frustration"
}

# ---------------- Audio Feature Extraction ----------------
def extract_audio_features(audio_path, target_dim=D_M_AUDIO):
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    mel = librosa.feature.melspectrogram(
        y=y, sr=sr, n_mels=target_dim,
        n_fft=512, hop_length=256
    )
    mel = librosa.power_to_db(mel, ref=np.max)
    return mel.T.astype(np.float32)  # (L, D)

# ---------------- Model Singleton ----------------
_model = None

def load_model():
    global _model
    if _model is not None:
        return _model

    spikformer = Spikformer(
        depths=NUM_LAYERS,
        tau=TAU,
        common_thr=COMMON_THR,
        dim=MODEL_DIM,
        T=SPIKE_T,
        heads=NUM_HEADS
    ).to(DEVICE)

    model = SpikEmo(
        dataset=DATASET,
        multi_attn_flag=MULTI_ATTN,
        roberta_dim=ROBERTA_DIM,
        hidden_dim=HIDDEN_DIM,
        dropout=DROPOUT,
        num_layers=NUM_LAYERS,
        model_dim=MODEL_DIM,
        num_heads=NUM_HEADS,
        D_m_audio=D_M_AUDIO,
        D_m_visual=D_M_VISUAL,
        D_g=D_G,
        D_p=D_P,
        D_e=D_E,
        D_h=D_H,
        n_classes=N_CLASSES,
        n_speakers=N_SPEAKERS,
        listener_state=LISTENER_STATE,
        context_attention=CONTEXT_ATTENTION,
        D_a=D_A,
        dropout_rec=DROPOUT_REC,
        device=DEVICE,
        spikformer_model=spikformer
    ).to(DEVICE)

    state = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
    model.load_state_dict(state, strict=False)
    model.eval()

    _model = model
    return model

# ---------------- Emotion Inference ----------------
def infer_emotion(audio_path: str):
    model = load_model()

    audio_feats = extract_audio_features(audio_path)
    L = audio_feats.shape[0]

    texts = torch.zeros((1, L, ROBERTA_DIM), device=DEVICE)
    audios = torch.tensor(audio_feats).unsqueeze(0).to(DEVICE)
    visuals = torch.zeros((1, L, D_M_VISUAL), device=DEVICE)

    speaker_masks = torch.zeros((1, L, 2), device=DEVICE)
    utterance_masks = torch.ones((1, L), device=DEVICE)
    padded_labels = torch.zeros((1, L), device=DEVICE).long()

    with torch.no_grad():
        _, _, _, _, logits = model(
            texts,
            audios,
            visuals,
            speaker_masks,
            utterance_masks,
            padded_labels
        )

        probs = F.softmax(logits, dim=-1)
        mean_probs = probs.mean(dim=0)

    probs_dict = {LABEL_MAP[i]: float(mean_probs[i]) for i in range(N_CLASSES)}
    pred_idx = mean_probs.argmax().item()

    return {
        "prediction": LABEL_MAP[pred_idx],
        "probabilities": probs_dict
    }
