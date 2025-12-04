from fastapi import HTTPException, UploadFile
from pathlib import Path
import shutil
import subprocess


def save_and_convert_audio(audio: UploadFile, user_id: str, request_id: str) -> str:
    # path to /temp directory
    bucket_dir = Path(__file__).resolve().parent.parent.parent / "temp"
    bucket_dir.mkdir(exist_ok=True)

    # find file extension
    extension = audio.content_type.split("/")[-1]
    file_path = bucket_dir / f"{user_id}-{request_id}.{extension}"

    # reset file pointer and save
    audio.file.seek(0)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # convert to mp3
    mp3_path = file_path.with_suffix(".mp3")

    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(file_path),
        str(mp3_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"FFmpeg conversion failed: {result.stderr}"
        )

    # delete original .webm file
    file_path.unlink(missing_ok=True)

    return mp3_path