from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
    error: Optional[str] = None

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
                timeout=60.0
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

async def generate_animation(task_id: str, prompt: str, options: dict):
    """Background task for animation generation."""
    output_dir = MEDIA_DIR / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "animation.mp4"

    generation_start = time.time()
    llm_start = time.time()
    used_fallback = False
    sanitization_changes = []

    try:
        # Generate code using LLM
        try:
            code = await generate_manim_code_with_llm(prompt)
            used_fallback = False
        except Exception as e:
            code = generate_manim_code(prompt)
            used_fallback = True
        finally:
            llm_time = time.time() - llm_start

        generation_tasks[task_id].update({
            "status": TaskStatus.PROCESSING,
            "code": code
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = Path(temp_dir) / "scene.py"
            code_file.write_text(code)
            print(f"Created temp file at: {code_file}")
            print(f"Code contents:\n{code}")
            
            quality_flag = "-ql" if options.get("quality") == "low" else "-qh"
            manim_cmd = [
                "manim",
                str(code_file),
                quality_flag,
                "--media_dir", str(MEDIA_DIR.absolute()),
                "--output_file", str(output_file.absolute())
            ]
            
            process = await asyncio.create_subprocess_exec(
                *manim_cmd,
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
                
            relative_path = output_file.relative_to(MEDIA_DIR)
            video_url = f"/videos/{relative_path}"
            
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

app = FastAPI(title="Manim Animation Generator",
             description="API for generating mathematical animations using Manim",
             version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store generated videos
MEDIA_DIR = Path("./media")
MEDIA_DIR.mkdir(exist_ok=True)

app.mount("/videos", StaticFiles(directory=str(MEDIA_DIR)), name="videos")
data_collector = DataCollector(Path("./training_data"), MEDIA_DIR)

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
        error=task_data.get("error")
    )

@app.get("/videos/{video_name}")
async def get_video(video_name: str):
    """Retrieve a generated video file."""
    video_path = MEDIA_DIR / video_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(str(video_path))

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