import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import uuid

# Support both package imports and running as a script
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(__file__))
    from schemas import FBDownloadRequest  # type: ignore
    from service import (  # type: ignore
        get_video_info,
        download_video,
        download_status,
    )
else:
    from .schemas import FBDownloadRequest
    from .service import (
        get_video_info,
        download_video,
        download_status,
    )


router = APIRouter()


@router.post("/video-info")
def facebook_video_info(request: FBDownloadRequest):
    try:
        return get_video_info(request.url, request.cookie)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting FB video info: {str(e)}")


@router.post("/download")
def facebook_start_download(request: FBDownloadRequest):
    download_id = str(uuid.uuid4())
    download_status[download_id] = {"status": "starting", "percent": "0%"}
    try:
        # Synchronous; clients can poll /progress
        file_path = download_video(request.url, request.format, request.quality, download_id, request.cookie)
        download_status[download_id]["status"] = "completed"
        download_status[download_id]["filename"] = file_path
        download_status[download_id]["percent"] = "100%"
        return {"download_id": download_id, "status": "completed"}
    except Exception as e:
        download_status[download_id] = {"status": "error", "error": str(e)}
        raise HTTPException(status_code=500, detail=f"FB download failed: {str(e)}")


@router.get("/progress/{download_id}")
def facebook_progress(download_id: str):
    if download_id not in download_status:
        raise HTTPException(status_code=404, detail="Download not found")
    return download_status[download_id]


@router.get("/download-file/{download_id}")
def facebook_download_file(download_id: str):
    if download_id not in download_status:
        raise HTTPException(status_code=404, detail="Download not found")
    status = download_status[download_id]
    if status.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Download not completed")
    file_path = status.get("filename")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")


