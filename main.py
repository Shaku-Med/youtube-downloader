from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import yt_dlp
import os
import asyncio
import uuid
from pathlib import Path
import json
from typing import Optional
import re

app = FastAPI(title="Advanced YouTube Downloader", version="1.0.0")

# Create downloads directory
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Store download progress
download_status = {}

class DownloadRequest(BaseModel):
    url: str
    format: str = "best"  # best, worst, mp3, mp4
    quality: str = "highest"  # highest, medium, lowest

class VideoInfo(BaseModel):
    title: str
    duration: int
    uploader: str
    view_count: int
    upload_date: str
    formats: list

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def progress_hook(d, download_id):
    """Progress callback for yt-dlp"""
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            download_status[download_id] = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta,
                'filename': d.get('filename', 'Unknown')
            }
        except:
            pass
    elif d['status'] == 'finished':
        # Store the filename for later retrieval
        filename = d.get('filename', '')
        if filename:
            download_status[download_id] = {
                'status': 'completed',
                'filename': filename,
                'percent': '100%'
            }
        else:
            download_status[download_id] = {
                'status': 'completed',
                'percent': '100%'
            }

async def get_video_info(url: str):
    """Extract video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_color': True,
        'extractor_retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get available formats
            formats = []
            if 'formats' in info:
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                        formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'quality': fmt.get('quality'),
                            'filesize': fmt.get('filesize'),
                            'vcodec': fmt.get('vcodec'),
                            'acodec': fmt.get('acodec'),
                            'resolution': fmt.get('resolution'),
                            'fps': fmt.get('fps')
                        })
            
            return VideoInfo(
                title=info.get('title', 'Unknown'),
                duration=info.get('duration', 0),
                uploader=info.get('uploader', 'Unknown'),
                view_count=info.get('view_count', 0),
                upload_date=info.get('upload_date', ''),
                formats=formats[:10]  # Limit to top 10 formats
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting video info: {str(e)}")

async def download_video(url: str, format_type: str, quality: str, download_id: str):
    """Download video with specified quality"""
    
    # Configure yt-dlp options based on format and quality
    if format_type == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOADS_DIR / f'{download_id}_%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320' if quality == 'highest' else '128',
            }],
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'nocheckcertificate': True,
            'no_color': True,
            'extractor_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
    else:
        # Video download options
        if quality == "highest":
            format_selector = 'bestvideo[height<=4320]+bestaudio/best[height<=4320]/best'  # 8K max, fallback to best
        elif quality == "4k":
            format_selector = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best'  # 4K max
        elif quality == "1080p":
            format_selector = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'  # 1080p max
        elif quality == "720p":
            format_selector = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'  # 720p max
        else:
            format_selector = 'worst[height>=360]'  # 360p min
            
        ydl_opts = {
            'format': format_selector,
            'outtmpl': str(DOWNLOADS_DIR / f'{download_id}_%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'merge_output_format': 'mp4',
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'no_color': True,
            'extractor_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the downloaded file - look for any file with the download_id prefix
        downloaded_files = list(DOWNLOADS_DIR.glob(f'{download_id}_*'))
        if downloaded_files:
            # Sort by modification time to get the most recent file
            downloaded_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            final_file = str(downloaded_files[0])
            print(f"Found file with download_id prefix: {final_file}")
            # Update download status with the final filename
            if download_id in download_status:
                download_status[download_id]['filename'] = final_file
            return final_file
        else:
            # If no files found with download_id prefix, look for recently created files
            all_files = list(DOWNLOADS_DIR.glob('*'))
            if all_files:
                # Get the most recently modified file
                latest_file = max(all_files, key=lambda x: x.stat().st_mtime)
                final_file = str(latest_file)
                print(f"Found latest file: {final_file}")
                # Update download status with the final filename
                if download_id in download_status:
                    download_status[download_id]['filename'] = final_file
                return final_file
            else:
                print(f"No files found in {DOWNLOADS_DIR}")
                raise Exception("Download completed but file not found")
            
    except Exception as e:
        download_status[download_id] = {
            'status': 'error',
            'error': str(e)
        }
        print(f"Download error for {download_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/")
async def get_interface(request: Request):
    """Serve the HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/video-info")
async def video_info_endpoint(request: DownloadRequest):
    """Get video information"""
    return await get_video_info(request.url)

@app.post("/download")
async def download_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start video download"""
    download_id = str(uuid.uuid4())
    
    # Initialize download status
    download_status[download_id] = {
        'status': 'starting',
        'percent': '0%'
    }
    
    # Start download in background
    background_tasks.add_task(
        download_video, 
        request.url, 
        request.format, 
        request.quality, 
        download_id
    )
    
    return {"download_id": download_id, "status": "started"}

@app.get("/progress/{download_id}")
async def get_progress(download_id: str):
    """Get download progress"""
    if download_id not in download_status:
        raise HTTPException(status_code=404, detail="Download not found")
    
    return download_status[download_id]

@app.get("/download-file/{download_id}")
async def download_file(download_id: str):
    """Download the completed file"""
    if download_id not in download_status:
        raise HTTPException(status_code=404, detail="Download not found")
    
    status = download_status[download_id]
    if status['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Download not completed")
    
    file_path = status.get('filename')
    
    # If filename is not in status, try to find the file
    if not file_path or not os.path.exists(file_path):
        # Look for files with download_id prefix
        downloaded_files = list(DOWNLOADS_DIR.glob(f'{download_id}_*'))
        if downloaded_files:
            downloaded_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            file_path = str(downloaded_files[0])
        else:
            # Look for recently created files
            all_files = list(DOWNLOADS_DIR.glob('*'))
            if all_files:
                latest_file = max(all_files, key=lambda x: x.stat().st_mtime)
                file_path = str(latest_file)
            else:
                raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)