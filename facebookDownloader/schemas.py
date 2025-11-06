from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FBDownloadRequest(BaseModel):
    url: str
    format: str = "mp4"  # mp4 or mp3
    quality: str = "highest"  # highest, 1080p, 720p, lowest
    cookie: Optional[str] = None


class FBFormat(BaseModel):
    format_id: Optional[str] = None
    ext: Optional[str] = None
    resolution: Optional[str] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    fps: Optional[int] = None


class FBVideoInfo(BaseModel):
    title: str
    duration: Optional[int] = None
    uploader: Optional[str] = None
    view_count: Optional[int] = 0
    upload_date: Optional[str] = None
    formats: List[FBFormat] = []


class FBProgress(BaseModel):
    status: str
    percent: Optional[str] = None
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

