from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from typing import Optional, Literal, TypedDict
import json
from pathlib import Path
import asyncio
from moviepy.editor import VideoFileClip


# Type definitions for documentation and type hints
class ExecutionOutcome(TypedDict):
    status: Optional[str]
    error: Optional[str]
    render_time: Optional[float]
    manim_stdout: Optional[str]
    manim_stderr: Optional[str]
    video_metadata: Optional[dict]

class GenerationMetadata(TypedDict):
    llm_response_time: Optional[float]
    used_fallback_template: bool
    sanitization_changes: list
    llm_config: dict

class GenerationAttempt(TypedDict):
    """Schema for generation attempts in JSONL files"""
    id: str
    timestamp: str
    model_version: str
    system_prompt: str
    user_query: str
    generated_code: str
    execution_outcome: ExecutionOutcome
    generation_metadata: GenerationMetadata
    user_feedback: Optional[bool]
    feedback_timestamp: Optional[str]
class DataCollector:
    def __init__(self, data_dir: Path, media_dir: Path):
        self.data_dir = data_dir
        self.media_dir = media_dir
        self.data_dir.mkdir(exist_ok=True)
        
    def _get_video_metadata(self, video_path: str) -> dict:
        """Extract metadata from generated video"""
        if not video_path:
            return None
            
        full_path = self.media_dir / video_path.replace("/videos/", "")
        if not full_path.exists():
            return None
            
        metadata = {
            "size_bytes": full_path.stat().st_size,
            "duration": None
        }
        
        try:
            with VideoFileClip(str(full_path)) as clip:
                metadata["duration"] = clip.duration
        except Exception as e:
            print(f"Failed to extract video duration: {e}")
            
        return metadata

    async def log_attempt(self, 
                        id: str, 
                        prompt: str, 
                        code: str, 
                        task_data: dict,
                        system_prompt: str,
                        generation_metadata: dict,
                        stdout: Optional[str] = None,
                        stderr: Optional[str] = None,
                        render_time: Optional[float] = None) -> None:
        """Log a generation attempt to disk"""
        # Create dictionary directly instead of using dataclass
        attempt = {
            "id": id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "model_version": "mistral",
            "system_prompt": system_prompt,
            "user_query": prompt,
            "generated_code": code,
            "execution_outcome": {
                "status": task_data["status"],
                "error": task_data.get("error"),
                "render_time": render_time,
                "manim_stdout": stdout,
                "manim_stderr": stderr,
                "video_metadata": self._get_video_metadata(task_data.get("video_url")) if task_data.get("video_url") else None
            },
            "generation_metadata": generation_metadata,
            "user_feedback": None,
            "feedback_timestamp": None
        }
        
        filename = self.data_dir / f"generation_attempts_{datetime.utcnow():%Y%m}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(attempt) + "\n")

    async def update_feedback(self, task_id: str, is_positive: bool, remove: bool = False) -> None:
        """Update an existing attempt with user feedback"""
        current_month_file = self.data_dir / f"generation_attempts_{datetime.utcnow():%Y%m}.jsonl"
        
        if not current_month_file.exists():
            raise ValueError(f"No generation file found for ID {task_id}")
                
        attempts = []
        found = False
        
        # Read all attempts
        with open(current_month_file, "r") as f:
            for line in f:
                attempt = json.loads(line)
                
                # If this is the attempt we want to update, add feedback
                if attempt.get('id') == task_id:
                    if remove:
                        attempt['user_feedback'] = None
                        attempt['feedback_timestamp'] = None
                    else:
                        attempt['user_feedback'] = is_positive
                        attempt['feedback_timestamp'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    
                attempts.append(attempt)
        
        if not found:
            raise ValueError(f"Generation {task_id} not found")
        
        # Write back all attempts
        with open(current_month_file, "w") as f:
            for attempt in attempts:
                f.write(json.dumps(attempt) + "\n")

# Utility functions for different learning approaches
def create_dpo_pairs(data_dir: Path) -> list[tuple[GenerationAttempt, GenerationAttempt]]:
    """Create preference pairs from attempts with same prompt"""
    attempts = []
    for file in data_dir.glob("generation_attempts_*.jsonl"):
        with open(file) as f:
            for line in f:
                attempts.append(GenerationAttempt(**json.loads(line)))
    
    # Group by query
    by_query = {}
    for attempt in attempts:
        by_query.setdefault(attempt.user_query, []).append(attempt)
    
    pairs = []
    for query_attempts in by_query.values():
        # Prioritize explicit user feedback over execution status
        positives = [a for a in query_attempts 
                    if a.user_feedback is True or 
                    (a.user_feedback is None and a.execution_outcome["status"] == "completed")]
        negatives = [a for a in query_attempts 
                    if a.user_feedback is False or
                    (a.user_feedback is None and a.execution_outcome["status"] == "failed")]
        
        for positive in positives:
            for negative in negatives:
                pairs.append((positive, negative))
    
    return pairs

def calculate_rlhf_reward(attempt: GenerationAttempt) -> float:
    """Calculate reward for RLHF training"""
    if attempt.execution_outcome["status"] == "completed":
        return 1.0
    elif attempt.execution_outcome["status"] == "failed":
        # Could have different penalties for different error types
        return -1.0
    return 0.0