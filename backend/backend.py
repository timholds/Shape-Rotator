from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from spaces_storage import SpacesStorage

from pydantic import BaseModel
import tempfile
import os
import uuid
from pathlib import Path
import asyncio
from typing import Optional
from enum import Enum
import httpx
import time
from collect_data import DataCollector
from pydantic import BaseModel
import logging
import shutil 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
SYSTEM_PROMPT_PATH = os.getenv('SYSTEM_PROMPT_PATH', 'backend/system_prompt.txt')
logger.info(f"Starting backend server with SYSTEM_PROMPT_PATH: {SYSTEM_PROMPT_PATH}")

def get_ollama_url() -> str:
    """Get the appropriate Ollama URL based on the environment."""
    # Check if running in Docker
    base_url = "http://ollama:11434" if os.environ.get("ENVIRONMENT") == "production" else "http://localhost:11434"
    return f"{base_url}/api/generate/mistral"  # Changed to use model-specific endpoint


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnimationRequest(BaseModel):
    prompt: str
    options: Optional[dict] = {
        "quality": "low",
        "resolution": "720p"
    }

class GenerationStatus(BaseModel):
    task_id: str
    status: TaskStatus
    code: Optional[str] = None
    video_url: Optional[str] = None
    code_url: Optional[str] = None 
    error: Optional[str] = None
    used_fallback: Optional[bool] = None 


class FeedbackRequest(BaseModel):
    task_id: str
    is_positive: bool
    remove: bool = False


def generate_manim_code(prompt: str) -> str:
    """Generate basic Manim code template."""
    class_name = sanitize_class_name(prompt)
    
    # Basic template for a Manim scene
    return f'''from manim import *

class {class_name}(Scene):
    def construct(self):
        text = Text("{prompt}")
        self.play(Write(text))
        self.wait()
'''

# TODO rename prompt here to user request
async def generate_manim_code_with_llm(prompt: str) -> str:
    """Generate Manim code using Ollama. Falls back to template if LLM fails."""
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        system_prompt = f.read()
    
    try:
        # ollama_url = get_ollama_url()
        # logger.info(f"Attempting to connect to Ollama at: {ollama_url}")  # Debug log
        print(f"Attempting to connect to Ollama at: {OLLAMA_HOST}")
        # async with httpx.AsyncClient() as client:
        async with httpx.AsyncClient(timeout=120.0) as client:
            try: 
                version_check = await client.get(f"{OLLAMA_HOST}/api/version")
                print(f"Version check response: {version_check.status_code}")
            except Exception as e:
                print(f"Version check failed: {str(e)}")

            print(f"Making generate request to: {OLLAMA_HOST}/api/generate")
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": "mistral",
                    "prompt": f"{system_prompt}\n\nUser request: {prompt}\n\nGenerate Manim code for this request.",
                    "stream": False
                },
                timeout=120.0
            )
      
            # Additional logging for debugging
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                print(f"Error response from Ollama: {response.status_code}")
                print(f"Response content: {response.text}")
                raise Exception(f"Ollama API returned status code {response.status_code}")
                              
            response.raise_for_status()
            result = response.json()
            return sanitize_manim_code(result['response'])

    except Exception as e:
        print(f"LLM generation failed: {str(e)}, falling back to template")
        # Fall back to template generation if LLM fails
        print(f"Full error details: {type(e).__name__}: {str(e)}")  # Enhanced error logging
        return generate_manim_code(prompt)

def sanitize_class_name(prompt: str) -> str:
    """Ensure the class name is a valid Python identifier."""
    sanitized = "".join(x for x in prompt.title() if x.isalnum())
    return f"Animation{sanitized}Scene" if not sanitized[0].isalpha() else f"{sanitized}Scene"

def sanitize_manim_code(code: str) -> str:
    """Clean and validate Manim code from LLM response.
    
    Args:
        code: Raw code string from LLM
        
    Returns:
        Cleaned and validated code string
        
    Removes markdown formatting, empty lines, and other artifacts.
    """
    code = code.strip()
    
    # Remove markdown code blocks if present
    if code.startswith("```python"):
        code = code[8:]  # Remove ```python
    if code.startswith("```"):
        code = code[3:]  # Remove ```
    if code.endswith("```"):
        code = code[:-3]  # Remove trailing ```
    
    # Clean up the code
    lines = code.split('\n')
    # Remove empty lines from the beginning
    while lines and not lines[0].strip():
        lines.pop(0)
    # Remove empty lines from the end    
    while lines and not lines[-1].strip():
        lines.pop()
    # Remove any standalone 'n' lines (artifact from newline processing)
    lines = [line for line in lines if line.strip() != 'n']
        
    return '\n'.join(lines)

app = FastAPI(title="Manim Animation Generator",
             description="API for generating mathematical animations using Manim",
             version="1.0.0")

# Set up static file serving for local videos
MEDIA_DIR = Path("./media")
MEDIA_DIR.mkdir(exist_ok=True)
(MEDIA_DIR / "videos").mkdir(exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(MEDIA_DIR / "videos")), name="videos")
spaces_client = SpacesStorage()

async def generate_animation(task_id: str, prompt: str, options: dict):
    """Background task for animation generation."""
    # output_dir = MEDIA_DIR / task_id
    output_dir = Path("./temp") / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "animation.mp4"

    generation_start = time.time()
    llm_start = time.time()
    used_fallback = False
    sanitization_changes = []

    try:
        generation_tasks[task_id].update({
            "status": TaskStatus.PROCESSING,
        })
        # Generate code using LLM
        try:
            code = await generate_manim_code_with_llm(prompt)
            used_fallback = False
        except Exception as e:
            code = generate_manim_code(prompt)
            used_fallback = True
        finally:
            llm_time = time.time() - llm_start

        code_url = await spaces_client.upload_code(code, task_id)
        if code_url is None:
            logger.warning(f"Failed to upload code for task {task_id}, continuing without code URL")


        generation_tasks[task_id].update({
            "code": code,
            "code_url": code_url,
            "used_fallback": used_fallback  # Use the existing variable

        })

         # If this is a fallback, use a static placeholder video instead
        if used_fallback and os.path.exists("./static/placeholder.mp4"):
            # Use a pre-generated placeholder
            static_video_url = f"https://{os.getenv('DOMAIN', 'theshaperotator.com')}/static/placeholder.mp4"
            
            generation_tasks[task_id].update({
                "status": TaskStatus.COMPLETED,
                "video_url": static_video_url
            })
            
            # Still log the attempt
            with open(SYSTEM_PROMPT_PATH, "r") as f:
                system_prompt = f.read()

            # Calculate total time
            render_time = time.time() - generation_start

            # Log the attempt with all metadata
            generation_metadata = {
                "llm_response_time": llm_time,
                "used_fallback_template": used_fallback,
                "sanitization_changes": sanitization_changes,
                "video_type": "static_placeholder",
                "llm_config": {
                    "model": "mistral",
                    "quality": options.get("quality", "low"),
                    "resolution": options.get("resolution", "720p")
                }
            }
            
            await data_collector.log_attempt(
                id=task_id,
                prompt=prompt,
                code=code,
                task_data=generation_tasks[task_id],
                system_prompt=system_prompt,
                generation_metadata=generation_metadata,
                stdout="Used static placeholder",
                stderr="",
                render_time=render_time
            )
            
            return  # Exit early, no need for video generation
        
        
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = Path(temp_dir) / "scene.py"
            code_file.write_text(code)
            print(f"Created temp file at: {code_file}")
            print(f"Code contents:\n{code}")
            
            quality_flag = "-ql" if options.get("quality") == "low" else "-qh"
            process = await asyncio.create_subprocess_exec(
                "manim",
                str(code_file),
                quality_flag,
                # "--media_dir", str(MEDIA_DIR.absolute()),
                # "--output_file", str(output_file.absolute())
                "--media_dir", str(output_dir.absolute()),
                "--output_file", str(output_file.absolute()),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode()
            stderr_text = stderr.decode()
            
            if process.returncode != 0:
                raise Exception(f"Manim error: {stderr_text}")
            
            if not output_file.exists():
                raise Exception("Video file not generated")
            
            # Upload to storage bucket
            video_url = await spaces_client.upload_video(output_file, task_id)
            if not video_url:
                raise Exception("Failed to upload video to storage")

            generation_tasks[task_id].update({
                "status": TaskStatus.COMPLETED,
                "video_url": video_url  
            })

            # Calculate total render time
            render_time = time.time() - generation_start

            # Read system prompt to log with the attempt
            with open(SYSTEM_PROMPT_PATH, "r") as f:
                system_prompt = f.read()

            # Log the attempt with all metadata
            generation_metadata = {
                "llm_response_time": llm_time,
                "used_fallback_template": used_fallback,
                "sanitization_changes": sanitization_changes,
                "llm_config": {
                    "model": "mistral",
                    "quality": options.get("quality", "low"),
                    "resolution": options.get("resolution", "720p")
                }
            }
            
            await data_collector.log_attempt(
                id=task_id,  # Add this line
                prompt=prompt,
                code=code,
                task_data=generation_tasks[task_id],
                system_prompt=system_prompt,
                generation_metadata=generation_metadata,
                stdout=stdout_text,
                stderr=stderr_text,
                render_time=render_time
            )

            # Clean up temporary files
            try:
                shutil.rmtree(output_dir)
            except Exception as cleanup_error:
                print(f"Warning during cleanup: {cleanup_error}")
                
    except Exception as e:
        error_str = str(e)
        print(f"Error generating animation: {error_str}")
        generation_tasks[task_id].update({
            "status": TaskStatus.FAILED,
            "error": error_str
        })

        # Log failed attempts too
        with open(SYSTEM_PROMPT_PATH, "r") as f:
            system_prompt = f.read()

        generation_metadata = {
            "llm_response_time": time.time() - llm_start,
            "used_fallback_template": used_fallback,
            "sanitization_changes": sanitization_changes,
            "llm_config": {
                "model": "mistral",
                "quality": options.get("quality", "low"),
                "resolution": options.get("resolution", "720p")
            }
        }

        await data_collector.log_attempt(
            id=task_id,  # Add this line
            prompt=prompt,
            code=code if 'code' in locals() else "",
            task_data=generation_tasks[task_id],
            system_prompt=system_prompt,
            generation_metadata=generation_metadata,
            stdout=stdout_text if 'stdout_text' in locals() else None,
            stderr=stderr_text if 'stderr_text' in locals() else None,
            render_time=time.time() - generation_start
        )

        try:
            if output_dir.exists():
                shutil.rmtree(output_dir)
        except Exception as cleanup_error:
            print(f"Warning during cleanup: {cleanup_error}")
async def cleanup_old_videos():
    """Remove videos older than 24 hours from storage bucket"""
    try:
        # List objects in bucket
        old_videos = await spaces_client.list_objects(
            prefix="videos/",
            older_than=datetime.now() - timedelta(hours=24)
        )
        for video in old_videos:
            await spaces_client.delete_object(video.key)
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://theshaperotator.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for collecting training data and feedback
TRAINING_DIR = Path("./training_data")
TRAINING_DIR.mkdir(exist_ok=True)

# Temporary directory for video generation
TEMP_DIR = Path("./temp")
TEMP_DIR.mkdir(exist_ok=True)

data_collector = DataCollector(TRAINING_DIR, TEMP_DIR)

# In-memory task storage
generation_tasks: dict[str, dict] = {}

@app.post("/generate", response_model=GenerationStatus)
async def create_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    """Create a new animation generation task."""
    task_id = str(uuid.uuid4())
    
    try:
        generation_tasks[task_id] = {
            "status": TaskStatus.PENDING,
            "code": None
        }
        
        background_tasks.add_task(
            generate_animation, 
            task_id, 
            request.prompt,
            request.options
        )
        
        return GenerationStatus(
            task_id=task_id,
            status=TaskStatus.PENDING
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=GenerationStatus)
async def get_status(task_id: str):
    """Get the status of an animation generation task."""
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = generation_tasks[task_id]
    return GenerationStatus(
        task_id=task_id,
        status=task_data["status"],
        code=task_data.get("code"),
        video_url=task_data.get("video_url"),
        code_url=task_data.get("code_url"),  # Include the code URL in the response
        error=task_data.get("error"),
        used_fallback=task_data.get("used_fallback", False)  # Include fallback status

    )

@app.get("/videos/{task_id}")
async def get_video(task_id: str):
    """Retrieve a generated video file."""
    # Check if task exists
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = generation_tasks[task_id]
    video_url = task_data.get("video_url")
    
    if not video_url:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # If it's a full URL (starts with http), it's stored in Spaces
    if video_url.startswith("http"):
        return RedirectResponse(url=video_url)
    
    # Otherwise, it's a local path
    local_path = MEDIA_DIR / video_url.lstrip("/")
    if not local_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(local_path)

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for a generated animation."""
    print("Received feedback request:", feedback.dict())  # Debug incoming request
    try:
        await data_collector.update_feedback(
            task_id=feedback.task_id,
            is_positive=feedback.is_positive,
            remove=feedback.remove
        )
        return {"status": "success",
                "message": "Feedback removed" if feedback.remove else "Feedback recorded",
                "feedback_type": "removed" if feedback.remove else ("positive" if feedback.is_positive else "negative")
        }
    except ValueError as e:
        print(f"ValueError in feedback submission: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Unexpected processing feedback submission: {str(e)}")
        # import traceback
        # print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)