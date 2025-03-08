import json
import os
import requests
import time
from pathlib import Path

def find_matching_code_with_llm(videos_file, transcripts_dir='transcripts', repo_dir='3b1b_repo'):
    """
    Find matching Manim code for videos using LLM assistance.
    
    Args:
        videos_file: Path to the JSON file with video metadata
        transcripts_dir: Directory containing video transcripts
        repo_dir: Path to the cloned 3b1b repository
    """
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    # Clone repository if needed
    clone_repo('https://github.com/3b1b/videos.git', repo_dir)
    
    # Group videos by year for more efficient processing
    videos_by_year = {}
    for video in videos:
        year = video['year']
        if year not in videos_by_year:
            videos_by_year[year] = []
        videos_by_year[year].append(video)
    
    # Process each year separately
    for year, year_videos in videos_by_year.items():
        print(f"\nProcessing videos from {year} ({len(year_videos)} videos)")
        
        # Get potential code directories for this year
        year_dirs = get_year_directories(repo_dir, year)
        if not year_dirs:
            print(f"  No matching directories found for {year}")
            continue
        
        # Process each video in this year
        for i, video in enumerate(year_videos):
            print(f"  Processing {i+1}/{len(year_videos)}: {video['title']}")
            
            # Get video transcript
            transcript = get_transcript(video['video_id'], transcripts_dir)
            
            # Call Ollama to find matches
            matches = find_matches_with_ollama(
                video, 
                transcript, 
                year_dirs, 
                repo_dir
            )
            
            # Update video with matches
            update_video_with_matches(video, matches)
    
    # Save updated metadata
    with open(f"{os.path.splitext(videos_file)[0]}_with_code.json", 'w') as f:
        json.dump(videos, f, indent=2)

def find_matches_with_ollama(video, transcript, year_dirs, repo_dir):
    """Use Ollama to find matches between video and code files."""
    
    # Create LLM context with video info and transcript excerpt
    video_context = {
        "title": video['title'],
        "id": video['video_id'],
        "description": video.get('description', ''),
        "transcript_excerpt": transcript[:1500] if transcript else "No transcript available"
    }
    
    matches = []
    
    # For each potential year directory, analyze code files
    for year_dir in year_dirs:
        # Get list of potential code files/directories
        potential_matches = get_potential_matches(year_dir)
        
        for match_path in potential_matches:
            # Get code content
            code_content = get_code_sample(match_path)
            if not code_content:
                continue
            
            # Prepare prompt for Ollama
            prompt = create_matching_prompt(video_context, match_path, code_content)
            
            # Query Ollama
            response = query_ollama(prompt)
            
            # Parse result to determine if it's a match and get supporting files
            match_result = parse_ollama_response(response)
            
            if match_result['is_match']:
                # Add to matches with confidence and any supporting files
                rel_path = os.path.relpath(match_path, repo_dir)
                matches.append({
                    'path': rel_path,
                    'type': 'directory' if os.path.isdir(match_path) else 'file',
                    'confidence': match_result['confidence'],
                    'evidence': match_result['evidence'],
                    'files': match_result['files']
                })
    
    # Sort matches by confidence
    matches.sort(key=lambda x: confidence_level(x['confidence']), reverse=True)
    return matches


def query_ollama(prompt, model="llama3"):
    """Send query to Ollama and get response."""
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return ""

def create_matching_prompt(video_context, code_path, code_content):
    """Create a prompt for matching a video to code."""
    code_type = "directory" if os.path.isdir(code_path) else "file"
    path_name = os.path.basename(code_path)
    
    prompt = f"""
You are an expert at matching 3Blue1Brown videos to their corresponding Manim code files.

VIDEO INFORMATION:
Title: {video_context['title']}
Video ID: {video_context['id']}
Description: {video_context['description']}

TRANSCRIPT EXCERPT:
{video_context['transcript_excerpt']}

CODE PATH: {code_path} ({code_type})

CODE CONTENT:
{code_content}

TASK:
Analyze if this {code_type} contains the Manim code for the video described above.

Answer the following questions:
1. Is this a match? (Yes/No/Maybe)
2. What evidence supports this conclusion? List specific terms, concepts, or code elements that match.
3. Confidence? (certain/high/medium/low)
4. If this is a directory, which files are most important for this video? List full relative paths.
5. Are there any supporting files from elsewhere that this code depends on? List full relative paths if known.

Return ONLY valid JSON in this exact format:
{{
  "is_match": true/false,
  "confidence": "certain/high/medium/low",
  "evidence": "Your explanation here",
  "files": ["file1.py", "file2.py"],
  "dependencies": ["path/to/dependency.py"]
}}


No additional text before or after the JSON.
"""
    return prompt


def parse_ollama_response(response):
    """Parse Ollama response to extract match information."""
    # Default result structure
    result = {
        "is_match": False,
        "confidence": "low",
        "evidence": "",
        "files": [],
        "dependencies": []
    }
    
    # Try to extract JSON from response
    try:
        # Find JSON pattern in response
        import re
        json_match = re.search(r'({[\s\S]*})', response)
        if json_match:
            json_str = json_match.group(1)
            parsed = json.loads(json_str)
            
            # Update result with parsed values
            result.update(parsed)
    except Exception as e:
        # If JSON parsing fails, use heuristics
        result["evidence"] = "Failed to parse response as JSON"
        if "yes" in response.lower():
            result["is_match"] = True
        if "certain" in response.lower():
            result["confidence"] = "certain"
        elif "high" in response.lower():
            result["confidence"] = "high"
        elif "medium" in response.lower():
            result["confidence"] = "medium"
    
    return result

def get_code_sample(path, max_files=3, max_lines=200):
    """Get sample code content for Ollama to analyze."""
    if os.path.isfile(path) and path.endswith('.py'):
        # Single file - read it directly
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""
    
    elif os.path.isdir(path):
        # Directory - sample from key files
        content = []
        
        # First look for main.py, scene.py or similar entry points
        entry_points = ['main.py', 'scene.py', os.path.basename(path) + '.py']
        for ep in entry_points:
            ep_path = os.path.join(path, ep)
            if os.path.exists(ep_path):
                try:
                    with open(ep_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content.append(f"# File: {ep}")
                        content.append(f.read())
                except Exception:
                    pass
        
        # If we don't have enough content, sample other Python files
        if not content:
            py_files = [f for f in os.listdir(path) if f.endswith('.py')]
            for i, pf in enumerate(py_files[:max_files]):
                try:
                    with open(os.path.join(path, pf), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # Take first portion of file
                        content.append(f"# File: {pf}")
                        content.append("".join(lines[:max_lines]))
                except Exception:
                    pass
        
        # Also look for README or description
        readme_files = [f for f in os.listdir(path) if 'readme' in f.lower() or 'description' in f.lower()]
        for rf in readme_files:
            try:
                with open(os.path.join(path, rf), 'r', encoding='utf-8', errors='ignore') as f:
                    content.append(f"# File: {rf}")
                    content.append(f.read())
            except Exception:
                pass
        
        return "\n\n".join(content)
    
    return ""


def get_code_sample(path, max_files=3, max_lines=200):
    """Get sample code content for Ollama to analyze."""
    if os.path.isfile(path) and path.endswith('.py'):
        # Single file - read it directly
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""
    
    elif os.path.isdir(path):
        # Directory - sample from key files
        content = []
        
        # First look for main.py, scene.py or similar entry points
        entry_points = ['main.py', 'scene.py', os.path.basename(path) + '.py']
        for ep in entry_points:
            ep_path = os.path.join(path, ep)
            if os.path.exists(ep_path):
                try:
                    with open(ep_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content.append(f"# File: {ep}")
                        content.append(f.read())
                except Exception:
                    pass
        
        # If we don't have enough content, sample other Python files
        if not content:
            py_files = [f for f in os.listdir(path) if f.endswith('.py')]
            for i, pf in enumerate(py_files[:max_files]):
                try:
                    with open(os.path.join(path, pf), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # Take first portion of file
                        content.append(f"# File: {pf}")
                        content.append("".join(lines[:max_lines]))
                except Exception:
                    pass
        
        # Also look for README or description
        readme_files = [f for f in os.listdir(path) if 'readme' in f.lower() or 'description' in f.lower()]
        for rf in readme_files:
            try:
                with open(os.path.join(path, rf), 'r', encoding='utf-8', errors='ignore') as f:
                    content.append(f"# File: {rf}")
                    content.append(f.read())
            except Exception:
                pass
        
        return "\n\n".join(content)
    
    return ""

