# Create test_upload.py in your backend container
from pathlib import Path
from spaces_storage import SpacesStorage
import asyncio

async def test_upload():
    # Create a small test file
    test_file = Path("/app/temp/test.mp4")
    test_file.write_bytes(b"test content")
    
    spaces = SpacesStorage()
    url = await spaces.upload_video(test_file, "test-task")
    print(f"Upload result: {url}")

asyncio.run(test_upload())