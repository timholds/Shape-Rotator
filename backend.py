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

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store generated videos
MEDIA_DIR = Path("./media")
MEDIA_DIR.mkdir(exist_ok=True)

class AnimationRequest(BaseModel):
    prompt: str
    options: Optional[dict] = None

class GenerationStatus(BaseModel):
    task_id: str
    status: str
    code: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None

# Store for tracking generation tasks
generation_tasks = {}

def generate_manim_code(prompt: str) -> str:
    """
    Placeholder for LLM integration.
    Will be replaced with actual LLM call.
    """
    # Generate a safe class name from the prompt
    safe_class_name = "".join(x for x in prompt.title() if x.isalnum()) + "Scene"
    
    return f'''from manim import *

class {safe_class_name}(Scene):
    def construct(self):
        # Basic animation example
        circle = Circle()
        self.play(Create(circle))
        self.wait()
'''

async def generate_animation(task_id: str, code: str):
    """
    Generates animation from Manim code and updates task status.
    """
    try:
        # Create temporary directory for Manim files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to temporary file
            code_file = Path(temp_dir) / "scene.py"
            code_file.write_text(code)
            
            # Run Manim
            process = await asyncio.create_subprocess_exec(
                "manim",
                str(code_file),
                "-qm",  # Medium quality
                "--media_dir", str(MEDIA_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Manim error: {stderr.decode()}")
            
            # Update task status with video location
            video_file = list(MEDIA_DIR.glob("*.mp4"))[-1]  # Get latest generated video
            generation_tasks[task_id].update({
                "status": "completed",
                "video_url": f"/videos/{video_file.name}"
            })
            
    except Exception as e:
        generation_tasks[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.post("/generate", response_model=GenerationStatus)
async def create_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Generate Manim code using placeholder function
        code = generate_manim_code(request.prompt)
        
        # Initialize task status
        generation_tasks[task_id] = {
            "status": "processing",
            "code": code
        }
        
        # Start animation generation in background
        background_tasks.add_task(generate_animation, task_id, code)
        
        return GenerationStatus(
            task_id=task_id,
            status="processing",
            code=code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=GenerationStatus)
async def get_status(task_id: str):
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = generation_tasks[task_id]
    return GenerationStatus(
        task_id=task_id,
        **task
    )

@app.get("/videos/{video_name}")
async def get_video(video_name: str):
    video_path = MEDIA_DIR / video_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(str(video_path))

# Cleanup endpoint (optional, for development)
@app.delete("/cleanup")
async def cleanup_media():
    """Remove all generated media files."""
    for file in MEDIA_DIR.glob("*"):
        if file.is_file():
            file.unlink()
    return {"status": "cleaned"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)