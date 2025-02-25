import pytest
import os
import asyncio
import sys
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch
from dotenv import load_dotenv

def pytest_sessionstart(session):
    """Load environment variables before any tests run."""
    # Find .env.development file
    dotenv_path = Path(__file__).parent.parent / ".env.development"
    
    print(f"Looking for .env file at: {dotenv_path.absolute()}")
    print(f"File exists: {dotenv_path.exists()}")
    
    if dotenv_path.exists():
        # Print file contents for debugging
        print("File content preview:")
        with open(dotenv_path) as f:
            for i, line in enumerate(f.readlines()[:5]):  # Print first 5 lines
                print(f"  Line {i+1}: {line.strip()}")
        
        # Try loading with dotenv
        result = load_dotenv(dotenv_path)
        print(f"load_dotenv result: {result}")
        
        # Check if vars are set after loading
        for var in ["SPACES_KEY", "SPACES_SECRET", "SPACES_BUCKET"]:
            print(f"{var} in env: {var in os.environ}")
            if var in os.environ:
                # Show first few chars for verification
                val = os.environ[var]
                print(f"  Value: {val[:5]}...")

# Debug info to help diagnose import issues
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

# Add parent directory to path for imports
#sys.path.insert(0, str(Path(__file__).parent.parent))


# Try imports with better error handling
try:
    from fastapi.testclient import TestClient
except ImportError:
    print("Warning: fastapi not installed, some tests may fail")
    TestClient = None

# Try to import your app and dependencies
# try:
#     from backend import app  # Import from backend.py
# except ImportError as e:
#     print(f"Warning: Failed to import backend app: {e}")
#     app = None

try:
    from spaces_storage import SpacesStorage  # Import from spaces_storage.py
except ImportError as e:
    print(f"Warning: Failed to import SpacesStorage: {e}")
    SpacesStorage = None

# Create a test client fixture if FastAPI is available
@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    if TestClient and app:
        return TestClient(app)
    return None

# Create a temporary directory for test files
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

# Create a test video file
@pytest.fixture
def video_file(temp_dir):
    """Create a test video file for uploads."""
    video_file = temp_dir / "test.mp4"
    video_file.write_bytes(b"test video content")
    yield video_file

# Mock SpacesStorage for unit tests
@pytest.fixture
def mock_spaces_storage():
    """Create a mocked SpacesStorage instance."""
    with patch('spaces_storage.SpacesStorage') as MockStorage:
        # Configure the mock
        instance = MockStorage.return_value
        instance.upload_video.return_value = asyncio.Future()
        instance.upload_video.return_value.set_result("https://test-bucket.sfo3.digitaloceanspaces.com/videos/test-task/animation.mp4")
        instance.get_video_url.return_value = asyncio.Future()
        instance.get_video_url.return_value.set_result("https://test-bucket.sfo3.digitaloceanspaces.com/videos/test-task/animation.mp4")
        yield instance


# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["SPACES_KEY"] = "test_key"
os.environ["SPACES_SECRET"] = "test_secret"
os.environ["SPACES_BUCKET"] = "test-bucket"

# Create a test client for your FastAPI app
@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

# Create a temporary directory for test files
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

# Create a test video file
@pytest.fixture
def test_video_file(temp_dir):
    """Create a test video file for uploads."""
    video_file = temp_dir / "test.mp4"
    
    # You can either create a dummy binary file
    video_file.write_bytes(b"test video content")
    
    # Or copy a real test video from your test assets
    # test_video_path = Path(__file__).parent / "assets" / "test_video.mp4"
    # shutil.copy(test_video_path, video_file)
    
    yield video_file

# Mock S3 (DigitalOcean Spaces)
@pytest.fixture
def mock_spaces():
    """Mock S3/Spaces service for testing."""
    with mock_s3():
        # Create the bucket
        s3 = boto3.resource('s3', 
                          region_name='sfo3',
                          endpoint_url='https://sfo3.digitaloceanspaces.com',
                          aws_access_key_id='test_key',
                          aws_secret_access_key='test_secret')
        s3.create_bucket(Bucket='test-bucket')
        yield s3

# Mock SpacesStorage for unit tests
@pytest.fixture
def mock_spaces_storage():
    """Create a mocked SpacesStorage instance."""
    with patch('spaces_storage.SpacesStorage') as MockStorage:
        # Configure the mock
        instance = MockStorage.return_value
        instance.upload_video.return_value = asyncio.Future()
        instance.upload_video.return_value.set_result("https://test-bucket.sfo3.digitaloceanspaces.com/videos/test-task/animation.mp4")
        instance.get_video_url.return_value = asyncio.Future()
        instance.get_video_url.return_value.set_result("https://test-bucket.sfo3.digitaloceanspaces.com/videos/test-task/animation.mp4")
        yield instance

# Mock Ollama API responses
@pytest.fixture
def mock_ollama_api():
    """Mock the Ollama API responses."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = asyncio.Future()
        mock_response.set_result({
            "response": """
from manim import *

class TestAnimationScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait(1)
"""
        })
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        yield mock_post