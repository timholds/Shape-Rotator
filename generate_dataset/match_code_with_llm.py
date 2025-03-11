import os
import json
import re
import requests
import time
from pathlib import Path
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler("matching.log"), 
                             logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Cache for LLM responses to avoid redundant calls
LLM_CACHE_FILE = "llm_response_cache.json"

def load_llm_cache():
    """Load the LLM response cache from file."""
    if os.path.exists(LLM_CACHE_FILE):
        try:
            with open(LLM_CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load LLM cache: {e}")
    return {}

def save_llm_cache(cache):
    """Save the LLM response cache to file."""
    try:
        with open(LLM_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        logger.warning(f"Failed to save LLM cache: {e}")

# Load the cache at module level
llm_cache = load_llm_cache()

def clone_repo(repo_url, target_dir):
    """Clone the 3b1b GitHub repository if it doesn't exist."""
    if not os.path.exists(target_dir):
        logger.info(f"Cloning repository {repo_url} to {target_dir}...")
        try:
            subprocess.run(['git', 'clone', repo_url, target_dir], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise
    else:
        logger.info(f"Repository already exists at {target_dir}, pulling latest changes...")
        try:
            subprocess.run(['git', '-C', target_dir, 'pull'], check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to pull latest changes: {e}")

def get_transcript(video_id, transcripts_dir):
    """Get the transcript for a video."""
    transcript_path = os.path.join(transcripts_dir, f"{video_id}_clean.txt")
    if not os.path.exists(transcript_path):
        logger.warning(f"Transcript not found for video {video_id}")
        return None
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading transcript for {video_id}: {e}")
        return None

def get_year_directories(repo_dir, year):
    """Get directories corresponding to a specific year."""
    year_patterns = [f"_{year}", f"{year}"]
    year_dirs = []
    
    for pattern in year_patterns:
        potential_dir = os.path.join(repo_dir, pattern)
        if os.path.exists(potential_dir) and os.path.isdir(potential_dir):
            year_dirs.append(potential_dir)
    
    # Optionally include adjacent years
    for adj_year in [int(year) - 1, int(year) + 1]:
        for pattern in [f"_{adj_year}", f"{adj_year}"]:
            potential_dir = os.path.join(repo_dir, pattern)
            if os.path.exists(potential_dir) and os.path.isdir(potential_dir):
                year_dirs.append(potential_dir)
    
    return year_dirs

def group_videos_by_series(videos):
    """Group videos that appear to be part of the same series."""
    series_groups = {}
    
    # Simple regex patterns for common series naming conventions
    series_patterns = [
        r'(.*?)\s*Part\s*(\d+)',
        r'(.*?)\s*#(\d+)',
        r'(.*?)\s*(\d+)\s*:',
        r'(DL\d+)',  # Deep Learning series
    ]
    
    for video in videos:
        title = video['title']
        series_name = None
        
        # Try to match series patterns
        for pattern in series_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                if pattern == r'(DL\d+)':  # Special case for DL series
                    series_name = "Deep Learning"
                else:
                    series_name = match.group(1).strip()
                break
        
        # If no series detected, use the video as its own group
        if not series_name:
            series_name = f"single_{video['video_id']}"
        
        if series_name not in series_groups:
            series_groups[series_name] = []
        
        series_groups[series_name].append(video)
    
    return series_groups

def analyze_dependencies(file_path, repo_dir):
    """Find imported dependencies in Python file."""
    dependencies = []
    if not file_path.endswith('.py'):
        return dependencies
    
    import_patterns = [
        r'from\s+([\w\.]+)\s+import',
        r'import\s+([\w\.]+)'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    import_path = match.group(1)
                    
                    # Handle relative imports within the repo
                    if import_path.startswith('_'):
                        # Convert import path to file path
                        file_path = import_path.replace('.', os.path.sep) + '.py'
                        full_path = os.path.join(repo_dir, file_path)
                        if os.path.exists(full_path):
                            dependencies.append(file_path)
                    
                    # Handle helpers and other local imports
                    helpers_match = re.search(r'from\s+(.*?)\.helpers\s+import', content)
                    if helpers_match:
                        base_path = helpers_match.group(1).replace('.', os.path.sep)
                        helpers_path = os.path.join(base_path, 'helpers.py')
                        full_helpers_path = os.path.join(repo_dir, helpers_path)
                        if os.path.exists(full_helpers_path):
                            dependencies.append(helpers_path)
    except Exception as e:
        logger.error(f"Error analyzing dependencies in {file_path}: {e}")
    
    return dependencies

def get_code_content(path, repo_dir, max_files=10):
    """Get code content for LLM analysis, including as much context as possible."""
    content_parts = []
    
    if os.path.isfile(path):
        # Single file
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content_parts.append(f"FILE: {os.path.relpath(path, repo_dir)}\n{f.read()}")
            
            # Also analyze dependencies
            deps = analyze_dependencies(path, repo_dir)
            for dep in deps:
                dep_path = os.path.join(repo_dir, dep)
                if os.path.exists(dep_path):
                    try:
                        with open(dep_path, 'r', encoding='utf-8', errors='replace') as f:
                            content_parts.append(f"DEPENDENCY: {dep}\n{f.read()}")
                    except Exception as e:
                        logger.error(f"Error reading dependency {dep}: {e}")
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
    
    elif os.path.isdir(path):
        # First, gather all Python files in the directory
        py_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        
        # Look for main entry points first
        priority_files = []
        regular_files = []
        
        basename = os.path.basename(path)
        main_patterns = ['main.py', 'scene.py', f'{basename}.py']
        
        for py_file in py_files:
            filename = os.path.basename(py_file)
            if filename in main_patterns:
                priority_files.append(py_file)
            else:
                regular_files.append(py_file)
        
        # Process files in priority order
        all_files = priority_files + regular_files
        processed_files = set()
        
        # Process up to max_files
        for i, file_path in enumerate(all_files):
            if i >= max_files:
                break
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    rel_path = os.path.relpath(file_path, repo_dir)
                    content_parts.append(f"FILE: {rel_path}\n{f.read()}")
                    processed_files.add(file_path)
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
        
        # Look for README or documentation files
        for root, _, files in os.walk(path):
            for file in files:
                if any(doc_type in file.lower() for doc_type in ['readme', 'description', '.md']):
                    doc_path = os.path.join(root, file)
                    try:
                        with open(doc_path, 'r', encoding='utf-8', errors='replace') as f:
                            rel_path = os.path.relpath(doc_path, repo_dir)
                            content_parts.append(f"DOC: {rel_path}\n{f.read()}")
                    except Exception as e:
                        logger.error(f"Error reading doc file {doc_path}: {e}")
    
    return "\n\n" + "="*80 + "\n\n".join(content_parts)

def pre_filter_candidates(video, code_path, repo_dir):
    """Quick checks to eliminate obvious non-matches."""
    video_id = video['video_id']
    title = video['title'].lower()
    video_year = video['year']
    
    # Check year range in path
    path_str = str(code_path)
    path_contains_year = False
    for year in range(video_year - 1, video_year + 2):  # Check year-1, year, year+1
        if f"_{year}" in path_str or f"/{year}" in path_str:
            path_contains_year = True
            break
    
    if not path_contains_year:
        return False
    
    # Try to read file/dir content for quick keyword check
    try:
        if os.path.isfile(code_path) and code_path.endswith('.py'):
            with open(code_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read().lower()
                
                # Very strong indicators - if present, accept immediately
                if video_id in content or f"youtube.com/watch?v={video_id}" in content:
                    return True
                
                # Extract meaningful words from title
                title_words = [w for w in title.split() if len(w) > 3 and w not in 
                              ['this', 'that', 'what', 'when', 'where', 'which', 'there', 'these', 'those']]
                
                # Check if multiple title words appear in content
                matches = sum(1 for word in title_words if word in content)
                if matches >= 2:  # At least 2 significant words match
                    return True
                    
        elif os.path.isdir(code_path):
            # For directories, check if the dirname is similar to video title
            dirname = os.path.basename(code_path).lower().replace('_', ' ')
            for word in title.split():
                if len(word) > 3 and word in dirname:
                    return True
                    
            # Check for title matches in README or main Python files
            for filename in os.listdir(code_path):
                if filename.endswith('.py') or filename.lower().startswith('readme'):
                    file_path = os.path.join(code_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read().lower()
                            if title in content or video_id in content:
                                return True
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Error in pre-filtering {code_path} for {video['title']}: {e}")
    
    # Default to keeping it as a candidate if we're not sure
    return True

def find_candidates(video, year_dirs, repo_dir):
    """Find candidate matches for a video based on simple heuristics."""
    candidates = []
    
    for year_dir in year_dirs:
        # Check directories first
        for item in os.listdir(year_dir):
            item_path = os.path.join(year_dir, item)
            
            # Apply pre-filtering
            if pre_filter_candidates(video, item_path, repo_dir):
                rel_path = os.path.relpath(item_path, repo_dir)
                candidates.append({
                    'path': rel_path,
                    'full_path': item_path,
                    'type': 'directory' if os.path.isdir(item_path) else 'file'
                })
    
    return candidates

def get_cache_key(video_id, code_path):
    """Generate a cache key for LLM responses."""
    key_str = f"{video_id}:{code_path}"
    return hashlib.md5(key_str.encode()).hexdigest()

def query_ollama_with_cache(prompt, video_id, code_path, model="deepseek-r1:32b"):
    """Query Ollama with caching of responses."""
    cache_key = get_cache_key(video_id, code_path)
    
    # Check cache
    if cache_key in llm_cache:
        logger.info(f"Using cached LLM response for {video_id} - {code_path}")
        return llm_cache[cache_key]
    
    # Not in cache, query Ollama
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    logger.info(f"Querying Ollama for {video_id} - {code_path}")
    try:
        response = requests.post(url, json=data, timeout=300)  # Long timeout for complex queries
        response.raise_for_status()
        result = response.json()
        response_text = result.get('response', '')
        
        # Store in cache
        llm_cache[cache_key] = response_text
        save_llm_cache(llm_cache)
        
        return response_text
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return ""

def create_matching_prompt(video, transcript, code_path, code_content):
    """Create a detailed prompt for the LLM to assess a match."""
    return f"""
You are an expert at matching 3Blue1Brown (3b1b) YouTube videos to their corresponding Manim code files.

TASK:
Determine if this code contains the Manim animation source for the given 3b1b video. 
There are cases where video does not have any code, like if the title contains "commencement" or "speech."


VIDEO INFORMATION:
Title: {video['title']}
Video ID: {video['video_id']}
Published: {video['published_at']}
Description: {video.get('description', 'N/A')}

TRANSCRIPT:
{transcript[:10000] if transcript else "No transcript available"}

CODE PATH: {code_path}

CODE CONTENT:
{code_content}

INSTRUCTIONS:
1. Analyze how well the code matches the video content.
2. Consider mathematical concepts, terminology, and specific animations.
3. Check for direct references to the video in comments, docstrings, etc.
4. Identify dependencies the code relies on.

Answer the following:
1. Is this a match? Respond with YES, LIKELY, UNLIKELY, or NO.
2. What evidence supports your conclusion? List specific matches between video and code.
3. If this is a directory, which files are most important for this video? List full paths.
4. Are there any supporting files/dependencies this code needs? List them.

IMPORTANT: Return your answer in VALID JSON format with the following structure:
{{
  "is_match": "YES/LIKELY/UNLIKELY/NO",
  "evidence": "Your detailed evidence here",
  "key_files": ["file1.py", "file2.py"],
  "dependencies": ["path/to/dependency.py"]
}}

ONLY return the JSON object - NO additional text.
"""

def parse_llm_response(response):
    """Parse LLM response, robustly extracting JSON."""
    # Default structure to return if parsing fails
    fallback = {
        "is_match": "UNLIKELY",
        "evidence": "Failed to parse response as JSON",
        "key_files": [],
        "dependencies": []
    }
    
    # Handle empty responses
    if not response or len(response.strip()) == 0:
        fallback["evidence"] = "Empty response from LLM"
        return fallback
        
    # Try to extract just the JSON object
    json_pattern = r'({[\s\S]*})'
    matches = re.search(json_pattern, response)
    
    if matches:
        json_str = matches.group(1)
        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            logger.warning("JSON parsing failed, attempting cleanup")
            
            # Try to clean up the JSON string
            # Replace common issues like unescaped newlines in strings
            cleaned = re.sub(r'(?<!\\)\\n', '\\\\n', json_str)
            cleaned = re.sub(r'(?<!\\)\\t', '\\\\t', cleaned)
            
            try:
                result = json.loads(cleaned)
                return result
            except json.JSONDecodeError:
                logger.warning("JSON cleanup failed, falling back to heuristics")
    
    # Fallback: Use heuristics to extract information
    logger.warning("Using heuristic fallback for LLM response parsing")
    
    # Default structure
    fallback = {
        "is_match": "UNLIKELY",
        "evidence": "Failed to parse response as JSON",
        "key_files": [],
        "dependencies": []
    }
    
    # Try to detect match status
    if re.search(r'\bYES\b', response, re.IGNORECASE):
        fallback["is_match"] = "YES"
    elif re.search(r'\bLIKELY\b', response, re.IGNORECASE):
        fallback["is_match"] = "LIKELY"
    elif re.search(r'\bUNLIKELY\b', response, re.IGNORECASE):
        fallback["is_match"] = "UNLIKELY"
    elif re.search(r'\bNO\b', response, re.IGNORECASE):
        fallback["is_match"] = "NO"
    
    # Try to extract file paths
    file_paths = re.findall(r'([a-zA-Z0-9_/]+\.py)', response)
    if file_paths:
        fallback["key_files"] = file_paths[:10]  # Limit to 10 files
        
    return fallback

def assess_match_with_llm(video, transcript, candidate, repo_dir):
    """Use LLM to assess if a candidate matches the video."""
    # Get full code content
    code_content = get_code_content(candidate['full_path'], repo_dir)
    
    # Create prompt
    prompt = create_matching_prompt(video, transcript, candidate['path'], code_content)
    
    # Query Ollama
    response = query_ollama_with_cache(prompt, video['video_id'], candidate['path'])
    
    # Parse response
    match_result = parse_llm_response(response)
    
    # Add the raw path information
    match_result['path'] = candidate['path']
    match_result['type'] = candidate['type']
    match_result['raw_response'] = response
    
    return match_result

def confidence_score(match_result):
    """Convert match status to numeric confidence score for sorting."""
    match_status = match_result.get('is_match', 'NO')
    
    if match_status == "YES":
        return 100
    elif match_status == "LIKELY":
        return 75
    elif match_status == "UNLIKELY":
        return 25
    else:  # NO or missing
        return 0

def find_matching_code_with_llm(videos_file, transcripts_dir='transcripts', repo_dir='3b1b_repo'):
    """
    Multi-stage approach to find matching code for videos using LLM assistance.
    """
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    # Clone repository if needed
    clone_repo('https://github.com/3b1b/videos.git', repo_dir)
    
    # Group videos by series for batch processing
    series_groups = group_videos_by_series(videos)
    logger.info(f"Grouped videos into {len(series_groups)} series")
    
    # Track all matches for final output
    all_matches = {}
    
    # Process each series
    for series_name, series_videos in series_groups.items():
        logger.info(f"Processing series: {series_name} ({len(series_videos)} videos)")
        
        # Get all relevant year directories for this series
        series_years = set(video['year'] for video in series_videos)
        all_year_dirs = []
        for year in series_years:
            all_year_dirs.extend(get_year_directories(repo_dir, year))
        all_year_dirs = list(set(all_year_dirs))  # Remove duplicates
        
        # Process each video in the series
        for video in series_videos:
            video_id = video['video_id']
            logger.info(f"Processing video: {video['title']} ({video_id})")
            
            # Get transcript
            transcript = get_transcript(video_id, transcripts_dir)
            
            # Find candidate matches
            candidates = find_candidates(video, all_year_dirs, repo_dir)
            logger.info(f"Found {len(candidates)} initial candidates")
            
            if not candidates:
                logger.warning(f"No candidates found for {video['title']}")
                continue
            
            # Assess each candidate with LLM
            # In find_matching_code_with_llm function, replace the sort line with:

            # Validate match results before sorting
            valid_match_results = []
            for result in match_results:
                if isinstance(result, dict) and 'path' in result:
                    # Ensure all required keys exist
                    if 'is_match' not in result:
                        result['is_match'] = 'UNLIKELY'
                    if 'evidence' not in result:
                        result['evidence'] = 'No evidence provided'
                    if 'key_files' not in result:
                        result['key_files'] = []
                    valid_match_results.append(result)
                else:
                    logger.warning(f"Skipping invalid match result: {result}")

            # Sort by confidence
            valid_match_results.sort(key=confidence_score, reverse=True)
            match_results = valid_match_results
            
            # Update video with best match
            best_match = match_results[0] if match_results else None
            if best_match and best_match['is_match'] in ["YES", "LIKELY"]:
                video['best_match'] = best_match['path']
                video['match_type'] = best_match['type']
                video['match_confidence'] = best_match['is_match']
                video['match_evidence'] = best_match['evidence']
                video['key_files'] = best_match.get('key_files', [])
                video['dependencies'] = best_match.get('dependencies', [])
                logger.info(f"Found {best_match['is_match']} match: {best_match['path']}")
            else:
                video['best_match'] = None
                video['match_type'] = None
                video['match_confidence'] = "NO"
                logger.info(f"No confident match found")
    
    # Save all detailed match results for analysis
    with open('all_match_results.json', 'w') as f:
        json.dump(all_matches, f, indent=2)
    
    # Save updated video metadata
    output_file = f"{os.path.splitext(videos_file)[0]}_with_code.json"
    with open(output_file, 'w') as f:
        json.dump(videos, f, indent=2)
    
    # Print summary
    matches_found = sum(1 for v in videos if v.get('best_match'))
    high_conf = sum(1 for v in videos if v.get('match_confidence') == "YES")
    med_conf = sum(1 for v in videos if v.get('match_confidence') == "LIKELY")
    
    logger.info(f"Matching complete. Found code for {matches_found}/{len(videos)} videos.")
    logger.info(f"High confidence (YES): {high_conf}")
    logger.info(f"Medium confidence (LIKELY): {med_conf}")
    logger.info(f"Match results saved to {output_file}")

def main():
    """Main entry point with command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Match 3Blue1Brown videos to Manim code using LLM')
    parser.add_argument('--videos', default='3b1b_videos.json', help='Path to video metadata JSON')
    parser.add_argument('--transcripts', default='transcripts', help='Directory containing transcripts')
    parser.add_argument('--repo', default='3b1b_repo', help='Path to cloned 3b1b repository')
    parser.add_argument('--model', default='deepseek-r1:32b', help='Ollama model to use')
    
    args = parser.parse_args()
    
    # Check if Ollama is running
    try:
        requests.get("http://localhost:11434/api/version", timeout=5)
    except requests.RequestException:
        logger.error("Ollama service is not running. Please start Ollama first.")
        return
    
    # Run the matching process
    find_matching_code_with_llm(args.videos, args.transcripts, args.repo)

if __name__ == '__main__':
    main()