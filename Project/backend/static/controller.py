from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

static_router = APIRouter()

@static_router.get("/temp/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files from temp directory"""
    print("**********************")
    # Validate filename to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Path to temp directory
    temp_dir = Path(__file__).resolve().parent.parent.parent / "temp"
    file_path = temp_dir / filename
    print(file_path)
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    print(file_path)
    # Return the file
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )