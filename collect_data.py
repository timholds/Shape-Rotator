from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal
import json
from pathlib import Path
import asyncio

@dataclass
class GenerationAttempt:
    # Core metadata
    timestamp: str
    model_version: str  # e.g. "mistral"
    system_prompt: str
    user_query: str
    
    # Generation details
    generated_code: str
    execution_outcome: dict[str, any]  # Status, stack trace, render time
    
    # Optional enrichments for different learning approaches
    extensions: Optional[dict] = None

class DataCollector:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
    async def log_attempt(self, 
                         prompt: str, 
                         code: str, 
                         task_data: dict,
                         system_prompt: str) -> None:
        """Log a generation attempt to disk"""
        attempt = GenerationAttempt(
            timestamp=datetime.utcnow().isoformat(),
            model_version="mistral",  # Get from your config
            system_prompt=system_prompt,
            user_query=prompt,
            generated_code=code,
            execution_outcome={
                "status": task_data["status"],
                "error": task_data.get("error"),
                # Could add render_time if you track it
            }
        )
        
        # Save to jsonl file
        filename = self.data_dir / f"generation_attempts_{datetime.utcnow():%Y%m}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(dataclasses.asdict(attempt)) + "\n")

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
    
    # Create success/failure pairs
    pairs = []
    for query_attempts in by_query.values():
        successes = [a for a in query_attempts 
                    if a.execution_outcome["status"] == "completed"]
        failures = [a for a in query_attempts 
                   if a.execution_outcome["status"] == "failed"]
        
        for success in successes:
            for failure in failures:
                pairs.append((success, failure))
    
    return pairs

def calculate_rlhf_reward(attempt: GenerationAttempt) -> float:
    """Calculate reward for RLHF training"""
    if attempt.execution_outcome["status"] == "completed":
        return 1.0
    elif attempt.execution_outcome["status"] == "failed":
        # Could have different penalties for different error types
        return -1.0
    return 0.0