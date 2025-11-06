import os
import re
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any


DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

download_status: Dict[str, Dict[str, Any]] = {}


def _sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def _base_headers(cookie: Optional[str]) -> Dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Mode": "navigate",
        "Referer": "https://www.facebook.com/",
    }
    if cookie:
        headers["Cookie"] = cookie
    return headers


def progress_hook(d: Dict[str, Any], download_id: str) -> None:
    if d.get("status") == "downloading":
        download_status[download_id] = {
            "status": "downloading",
            "percent": d.get("_percent_str", "0%"),
            "speed": d.get("_speed_str", "N/A"),
            "eta": d.get("_eta_str", "N/A"),
            "filename": d.get("filename"),
        }
    elif d.get("status") == "finished":
        filename = d.get("filename")
        download_status[download_id] = {
            "status": "completed",
            "percent": "100%",
            "filename": filename,
        }


def get_video_info(url: str, cookie: Optional[str] = None) -> Dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "extractor_retries": 3,
        "http_headers": _base_headers(cookie),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for fmt in info.get("formats", []) or []:
            if fmt.get("vcodec") != "none" or fmt.get("acodec") != "none":
                formats.append(
                    {
                        "format_id": fmt.get("format_id"),
                        "ext": fmt.get("ext"),
                        "quality": fmt.get("quality"),
                        "filesize": fmt.get("filesize"),
                        "vcodec": fmt.get("vcodec"),
                        "acodec": fmt.get("acodec"),
                        "resolution": fmt.get("resolution"),
                        "fps": fmt.get("fps"),
                    }
                )
        return {
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "view_count": info.get("view_count", 0),
            "upload_date": info.get("upload_date"),
            "formats": formats[:10],
        }


def _format_selector_for_quality(quality: str) -> str:
    if quality == "highest":
        return "bestvideo+bestaudio/best"
    if quality == "1080p":
        return "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    if quality == "720p":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
    return "worst[height>=360]"


def download_video(url: str, format_type: str, quality: str, download_id: str, cookie: Optional[str] = None) -> str:
    if format_type == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            # Use short, safe filenames to avoid Windows path/charset issues
            "outtmpl": str(DOWNLOADS_DIR / f"{download_id}_%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320" if quality == "highest" else "128",
                }
            ],
            "progress_hooks": [lambda d: progress_hook(d, download_id)],
            "nocheckcertificate": True,
            "no_color": True,
            "extractor_retries": 3,
            "http_headers": _base_headers(cookie),
            "restrictfilenames": True,
            "windowsfilenames": True,
        }
    else:
        ydl_opts = {
            "format": _format_selector_for_quality(quality),
            # Use short, safe filenames to avoid Windows path/charset issues
            "outtmpl": str(DOWNLOADS_DIR / f"{download_id}_%(id)s.%(ext)s"),
            "progress_hooks": [lambda d: progress_hook(d, download_id)],
            "merge_output_format": "mp4",
            "prefer_ffmpeg": True,
            "keepvideo": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "ignoreerrors": False,
            "nocheckcertificate": True,
            "no_color": True,
            "extractor_retries": 3,
            "http_headers": _base_headers(cookie),
            "restrictfilenames": True,
            "windowsfilenames": True,
        }

    download_status[download_id] = {"status": "starting", "percent": "0%"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # try to find output file
    candidates = list(DOWNLOADS_DIR.glob(f"{download_id}_*"))
    if candidates:
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        chosen = str(candidates[0])
        if download_id in download_status:
            download_status[download_id]["filename"] = chosen
        return chosen
    # fallback to latest file
    all_files = list(DOWNLOADS_DIR.glob("*"))
    if not all_files:
        raise RuntimeError("Download completed but file not found")
    chosen = str(max(all_files, key=lambda p: p.stat().st_mtime))
    if download_id in download_status:
        download_status[download_id]["filename"] = chosen
    return chosen

