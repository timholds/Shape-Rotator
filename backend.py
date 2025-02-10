from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
from pathlib import Path
import asyncio
from typing import Optional
from enum import Enum

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

# In-memory task storage - in production, this should be a proper database
generation_tasks: dict[str, dict] = {}

def sanitize_class_name(prompt: str) -> str:
    """Ensure the class name is a valid Python identifier."""
    # Remove non-alphanumeric characters and ensure starts with a letter
    sanitized = "".join(x for x in prompt.title() if x.isalnum())
    return f"Animation{sanitized}Scene" if not sanitized[0].isalpha() else f"{sanitized}Scene"

def generate_manim_code(prompt: str, options: dict) -> str:
    """Generate Manim code based on prompt and options."""
    class_name = sanitize_class_name(prompt)
    
    # For now, just return a minimal working example
    return f'''from manim import *

class {class_name}(Scene):
    def construct(self):
        text = Text("Hello, Manim!")
        self.play(Write(text))
        self.wait()
'''

async def generate_animation(task_id: str, code: str, options: dict):
    """Background task for animation generation."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = Path(temp_dir) / "scene.py"
            code_file.write_text(code)
            
            # Update task status
            generation_tasks[task_id]["status"] = TaskStatus.PROCESSING
            
            # Mock video generation for now
            await asyncio.sleep(2)  # Simulate processing time
            
            # In reality, we'd run Manim here
            # process = await asyncio.create_subprocess_exec(...)
            
            # For now, just update task as completed
            generation_tasks[task_id].update({
                "status": TaskStatus.COMPLETED,
                "video_url": f"/videos/example.mp4"  # Mock URL
            })
            
    except Exception as e:
        generation_tasks[task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e)
        })

@app.post("/generate", response_model=GenerationStatus)
async def create_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    """Create a new animation generation task."""
    task_id = str(uuid.uuid4())
    
    try:
        code = generate_manim_code(request.prompt, request.options)
        
        generation_tasks[task_id] = {
            "status": TaskStatus.PENDING,
            "code": code
        }
        
        background_tasks.add_task(
            generate_animation, 
            task_id, 
            code, 
            request.options
        )
        
        return GenerationStatus(
            task_id=task_id,
            status=TaskStatus.PENDING,
            code=code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=GenerationStatus)
async def get_status(task_id: str):
    """Get the status of an animation generation task."""
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return GenerationStatus(task_id=task_id, **generation_tasks[task_id])

@app.get("/videos/{video_name}")
async def get_video(video_name: str):
    """Retrieve a generated video file."""
    video_path = MEDIA_DIR / video_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(str(video_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)