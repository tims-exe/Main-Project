import whisper
import os

_model = whisper.load_model("base")

# Get project root (parent of engine/)
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ENGINE_DIR, "..", ".."))

AUDIO_BASE_DIR = os.path.join(PROJECT_ROOT, "temp")

def transcribe_audio(audio_ref: str) -> str:
    """
    Transcribe an audio file using local Whisper.
    Automatically appends .mp3 if no extension is provided.
    """
    try:
        # Append .mp3 if missing extension
        if not os.path.splitext(audio_ref)[1]:
            audio_ref = f"{audio_ref}.mp3"

        audio_path = audio_ref

        # Resolve relative paths
        if not os.path.isabs(audio_ref):
            audio_path = os.path.join(AUDIO_BASE_DIR, audio_ref)

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = _model.transcribe(audio_path)
        return result.get("text", "").strip()

    except Exception as e:
        print(f"Whisper transcription error: {e}")
        return ""
