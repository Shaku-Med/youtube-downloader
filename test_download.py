import os
from pathlib import Path
import uuid

DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

def test_file_finding():
    download_id = str(uuid.uuid4())
    
    # Create a test file
    test_file = DOWNLOADS_DIR / f"{download_id}_test_video.mp4"
    test_file.write_text("test content")
    
    print(f"Created test file: {test_file}")
    
    # Test the file finding logic
    downloaded_files = list(DOWNLOADS_DIR.glob(f'{download_id}_*'))
    if downloaded_files:
        downloaded_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        final_file = str(downloaded_files[0])
        print(f"Found file with download_id prefix: {final_file}")
        return final_file
    else:
        all_files = list(DOWNLOADS_DIR.glob('*'))
        if all_files:
            latest_file = max(all_files, key=lambda x: x.stat().st_mtime)
            final_file = str(latest_file)
            print(f"Found latest file: {final_file}")
            return final_file
        else:
            print(f"No files found in {DOWNLOADS_DIR}")
            return None

if __name__ == "__main__":
    result = test_file_finding()
    print(f"Test result: {result}")
    
    # Clean up
    for file in DOWNLOADS_DIR.glob("*"):
        if file.is_file():
            file.unlink()
    print("Test completed and cleaned up.") 