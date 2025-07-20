# YouTube Downloader Pro

A powerful, user-friendly web application that makes downloading YouTube videos and playlists simple and efficient. Whether you need a single video in 4K or an entire playlist for offline viewing, this tool has you covered.

## What Makes This Special

We've built this downloader with real users in mind. It handles everything from individual videos to complete playlists, supports resolutions up to 8K, and gives you real-time progress updates so you're never left wondering what's happening.

**Key Highlights:**
- Download videos up to 8K quality (4320p) when available
- Extract audio-only files in MP3 format
- Handle entire YouTube playlists effortlessly
- Watch download progress in real-time with speed and time estimates
- Clean, responsive interface that works on any device
- Robust error handling that actually tells you what went wrong

## Getting Started

### What You'll Need

Before diving in, make sure you have these essentials:

**Python 3.8 or newer** - This powers the entire application
**FFmpeg** - Handles all the video/audio processing magic
- **Windows users**: Grab it from [FFmpeg's website](https://ffmpeg.org/download.html)
- **Mac users**: Run `brew install ffmpeg` in Terminal
- **Linux users**: Try `sudo apt install ffmpeg` (Ubuntu/Debian)

### Setting Everything Up

Getting this running is straightforward:

1. **Get the code** - Download or clone this project to your computer

2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Double-check FFmpeg** by running:
   ```bash
   ffmpeg -version
   ```
   If you see version information, you're good to go!

## How to Use It

### Starting the Application

1. **Fire up the server**:
   ```bash
   python main.py
   ```

2. **Open your browser** and go to `http://localhost:8000`

That's it! You'll see a clean interface ready for action.

### Downloading Your Content

The process is designed to be intuitive:

1. **Paste your YouTube URL** - Works with individual videos or entire playlists
2. **Pick your format** - Video (MP4) or audio-only (MP3)
3. **Choose quality** - From 8K down to mobile-friendly resolutions
4. **Preview first** - Hit "Get Video Info" to see what you're downloading
5. **Start the download** - Click the appropriate download button and watch the progress

### Quality Options Explained

We've simplified the quality selection:
- **Highest Available** - Gets the best quality possible (up to 8K if available)
- **4K (2160p)** - Perfect for large screens and future-proofing
- **Full HD (1080p)** - The sweet spot for most users
- **HD (720p)** - Great balance of quality and file size
- **Lower Quality** - Smaller files for limited storage or slower connections

## For Developers: API Reference

If you want to integrate this into your own projects, we've built a clean REST API:

### Core Endpoints

**`GET /`** - Serves the web interface

**`POST /video-info`** - Get video details without downloading
```json
{
  "url": "https://youtube.com/watch?v=example"
}
```

**`POST /download`** - Start a download
```json
{
  "url": "https://youtube.com/watch?v=example",
  "format": "mp4",
  "quality": "highest"
}
```

**`GET /progress/{download_id}`** - Check download status

**`GET /download-file/{download_id}`** - Retrieve completed file

## Under the Hood

We've built this on a solid foundation of modern technologies:

**Backend Stack:**
- **FastAPI** - Fast, modern Python web framework
- **yt-dlp** - The most capable YouTube downloader available
- **Pydantic** - Ensures data integrity and validation
- **Uvicorn** - Production-ready ASGI server

**Key Technical Decisions:**
- Downloads run in the background so the interface stays responsive
- Each download gets a unique ID to prevent conflicts
- Progress tracking happens through efficient polling
- Comprehensive error handling provides meaningful feedback

## Customization and Configuration

### Environment Setup
The application works great out of the box, but you can customize:

- **Host/Port**: Edit `main.py` to change where the server runs
- **Download Location**: Modify `DOWNLOADS_DIR` to save files elsewhere
- **Performance**: The app handles multiple downloads simultaneously

### File Organization
Downloaded files are automatically organized with:
- Unique identifiers to prevent naming conflicts
- Sanitized filenames for cross-platform compatibility
- Automatic cleanup of temporary files

## Troubleshooting Common Issues

**"FFmpeg not found" errors:**
This usually means FFmpeg isn't installed or isn't in your system's PATH. Double-check the installation and try running `ffmpeg -version` in your terminal.

**Downloads keep failing:**
- Verify your internet connection is stable
- Make sure the YouTube URL is valid and the video is publicly accessible
- Check that you have enough disk space in your downloads folder

**Permission-related errors:**
Ensure the application has write permissions to the downloads directory. On some systems, you might need to run with elevated privileges.

## A Note on Responsible Use

We've designed this tool for personal use and educational purposes. Please respect content creators' rights and YouTube's Terms of Service. When in doubt, consider supporting creators through official channels.

## Project Structure

```
YOUTUBE CODE/
├── main.py                 # Main application logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── downloads/             # Your downloaded files end up here
└── README.md             # This guide
```

## Contributing and Support

Found a bug or have an idea for improvement? We'd love to hear from you. The codebase is designed to be extensible - adding new features or formats is straightforward.

For technical support, check the troubleshooting section first, then feel free to open an issue with details about your problem.