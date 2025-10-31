import os
import re
import csv
import shutil
import sys
import subprocess
import json
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading




import torchaudio
import av  # PyAV (pip install av)

# ==================== USER CONFIG ====================
DATA_ROOT = Path("data")
OUTPUT_ROOT = Path("data_sorted")
CSV_PATH = OUTPUT_ROOT / "dataset_index.csv"
MOVE_FILES = False  # if True, move instead of copy
NUM_WORKERS = 8
DURATION_TOLERANCE = 0.2  # seconds tolerance for mismatch
# =====================================================

TARGET_EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad']

RAVDESS_EMOTION_MAP = {
    "01": "neutral",
    "02": "neutral",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fear",
    "07": "disgust",
    "08": None
}

CREMAD_EMOTION_MAP = {
    "ANG": "angry",
    "DIS": "disgust",
    "FEA": "fear",
    "HAP": "happy",
    "NEU": "neutral",
    "SAD": "sad"
}

gpu_lock = threading.Lock()


# =============== UTILITIES ===============
def transfer_file(src: Path, dst: Path, move=False):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(str(src), str(dst))
    return str(dst)


def get_audio_duration(file_path: Path) -> float:
    try:
        info = torchaudio.info(str(file_path))
        return info.num_frames / info.sample_rate
    except Exception:
        return -1.0


def get_video_duration(file_path: Path) -> float:
    try:
        with av.open(str(file_path)) as container:
            return float(container.duration / av.time_base)
    except Exception:
        return -1.0


def durations_match(audio_file, video_file) -> bool:
    ad = get_audio_duration(audio_file)
    vd = get_video_duration(video_file)
    if ad < 0 or vd < 0:
        return False
    return abs(ad - vd) <= DURATION_TOLERANCE


def parse_ravdess_emotion(file_stem):
    parts = file_stem.split("-")
    if len(parts) < 7:
        return None
    emo_code = parts[2]
    return RAVDESS_EMOTION_MAP.get(emo_code, None)


def parse_cremad_emotion(file_stem):
    match = re.match(r"(\d+)_([A-Z]{3})_(?P<emo>[A-Z]{3})_.*", file_stem)
    if not match:
        return None
    emo_code = match.group("emo")
    return CREMAD_EMOTION_MAP.get(emo_code, None)


# ================= VIDEO CONVERSION =================
def get_codec_info(video_path: Path):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "json", str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        if "streams" not in info or not info["streams"]:
            return None
        codec = info["streams"][0]["codec_name"]
        return codec
    except Exception:
        return None


def convert_flv_to_mp4(src: Path, dst: Path, prefer_remux=True, gpu_lock=gpu_lock):
    """Convert or remux FLV → MP4 (lossless if possible)."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Inspect codec
    try:
        probe = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=codec_name", "-of", "default=nw=1:nk=1", str(src)],
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        probe = None

    # If already H.264, just remux (no re-encode)
    if prefer_remux and probe == "h264":
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)
        ]
    else:
        # Use GPU for one job at a time
        with gpu_lock:
            cmd = [
                "ffmpeg", "-y",
                "-hwaccel", "cuda",
                "-i", str(src),
                "-c:v", "h264_nvenc",
                "-preset", "p7",
                "-cq", "0",
                "-c:a", "aac",
                "-b:a", "192k",
                str(dst)
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ GPU encode failed for {src.name}, retrying CPU remux...")
                cmd = [
                    "ffmpeg", "-y", "-i", str(src),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)
                ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(dst)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Conversion failed for {src.name}: {e}")
        return None


# =============== DATA GATHERING ===============
def gather_cremad_pairs():
    pairs = []
    audio_root = DATA_ROOT / "crema-d-mirror" / "AudioWAV"
    video_root = DATA_ROOT / "crema-d-mirror" / "VideoFlash"
    video_dict = {v.stem: v for ext in ("*.flv", "*.mp4") for v in video_root.glob(ext)}

    for audio_file in audio_root.glob("*.wav"):
        if audio_file.stem in video_dict:
            video_file = video_dict[audio_file.stem]
            emotion = parse_cremad_emotion(audio_file.stem)
            if emotion in TARGET_EMOTIONS:
                pairs.append((audio_file, video_file, emotion))
    return pairs


def gather_ravdess_pairs():
    pairs = []
    audio_root = DATA_ROOT / "Ravdess" / "audio"
    video_root = DATA_ROOT / "Ravdess" / "video"
    audio_dict = {}
    for actor_dir in audio_root.glob("Actor_*"):
        for a in actor_dir.glob("*.wav"):
            parts = a.stem.split("-")
            if len(parts) < 7:
                continue
            key = "-".join(parts[1:])
            audio_dict[key] = a

    for actor_dir in video_root.glob("Actor_*"):
        for v in actor_dir.glob("*.mp4"):
            parts = v.stem.split("-")
            if len(parts) < 7:
                continue
            key = "-".join(parts[1:])
            if key in audio_dict:
                a = audio_dict[key]
                emotion = parse_ravdess_emotion(v.stem)
                if emotion in TARGET_EMOTIONS:
                    pairs.append((a, v, emotion))
    return pairs


# =============== ORGANIZATION ===============
def organize_and_index():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    crema_pairs = gather_cremad_pairs()
    ravdess_pairs = gather_ravdess_pairs()
    all_pairs = crema_pairs + ravdess_pairs

    print(f"📦 Found {len(all_pairs)} total (CREMA-D + RAVDESS) audio-video pairs.\n")

    emotion_counters = defaultdict(int)
    csv_entries = []

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as ex:
        futures = []

        for audio, video, emotion in all_pairs:
            emotion_counters[emotion] += 1
            idx = emotion_counters[emotion]

            # Destination filenames match
            base_name = f"{emotion}_{idx:05d}"
            audio_dst = OUTPUT_ROOT / emotion / "audio" / f"{base_name}.wav"
            video_dst = OUTPUT_ROOT / emotion / "video" / f"{base_name}.mp4"

            if video.suffix.lower() == ".flv":
                futures.append(ex.submit(convert_flv_to_mp4, video, video_dst))
            else:
                futures.append(ex.submit(transfer_file, video, video_dst, MOVE_FILES))
            futures.append(ex.submit(transfer_file, audio, audio_dst, MOVE_FILES))

            csv_entries.append([str(audio_dst), str(video_dst), emotion])

        for f in as_completed(futures):
            _ = f.result()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["audio_path", "video_path", "emotion"])
        writer.writerows(csv_entries)

    print(f"\n✅ Sorting & conversion complete. Saved to: {OUTPUT_ROOT.resolve()}")
    print(f"🧾 Metadata index: {CSV_PATH.resolve()}\n")
    print("📊 Emotion-wise file counts:")
    for emo in TARGET_EMOTIONS:
        print(f"{emo:<8}: {emotion_counters.get(emo, 0)}")


if __name__ == "__main__":
    organize_and_index()

# python sort_data.py