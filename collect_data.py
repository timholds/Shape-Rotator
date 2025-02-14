from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Literal
import json
from pathlib import Path
import asyncio
from moviepy.editor import VideoFileClip


@dataclass
class GenerationAttempt:
    # Core metadata
    id: str
    timestamp: str
    model_version: str  # e.g. "mistral"
    system_prompt: str
    user_query: str
    
    # Generation details
    generated_code: str
    # Enhanced execution outcome
    execution_outcome: dict[str, any] = field(default_factory=lambda: {
        "status": None,
        "error": None,
        "render_time": None,
        "manim_stdout": None,
        "manim_stderr": None,
        "video_metadata": None,
    })

    # Generation metadata
    generation_metadata: dict[str, any] = field(default_factory=lambda: {
        "llm_response_time": None,
        "used_fallback_template": False,
        "sanitization_changes": [],
        "llm_config": {}
    })
    
    # Feedback data
    user_feedback: Optional[bool] = None
    feedback_timestamp: Optional[str] = None


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
        attempt = GenerationAttempt(
            id=id,
            timestamp=datetime.utcnow().isoformat(),
            model_version="mistral",
            system_prompt=system_prompt,
            user_query=prompt,
            generated_code=code,
            execution_outcome={
                "status": task_data["status"],
                "error": task_data.get("error"),
                "render_time": render_time,
                "manim_stdout": stdout,
                "manim_stderr": stderr,
                "video_metadata": self._get_video_metadata(task_data.get("video_url")) if task_data.get("video_url") else None
            },
            generation_metadata=generation_metadata
        )
        
        filename = self.data_dir / f"generation_attempts_{datetime.utcnow():%Y%m}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(asdict(attempt)) + "\n")

    async def update_feedback(self, task_id: str, is_positive: bool) -> None:
        """Update an existing attempt with user feedback"""
        current_month_file = self.data_dir / f"generation_attempts_{datetime.utcnow():%Y%m}.jsonl"
        
        if not current_month_file.exists():
            raise ValueError(f"No generation file found for ID {task_id}")
            
        attempts = []
        found = False
        
        # Read all attempts
        with open(current_month_file, "r") as f:
            for line in f:
                attempt = GenerationAttempt(**json.loads(line))
                if attempt.id == task_id:
                    attempt.user_feedback = is_positive
                    attempt.feedback_timestamp = datetime.utcnow().isoformat()
                    found = True
                attempts.append(attempt)
        
        if not found:
            raise ValueError(f"Generation {task_id} not found")
        
        # Write back all attempts
        with open(current_month_file, "w") as f:
            for attempt in attempts:
                f.write(json.dumps(asdict(attempt)) + "\n")

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