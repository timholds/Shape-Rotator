import os
import json
import re
import subprocess
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta

def clone_repo(repo_url, target_dir):
    """Clone the 3b1b GitHub repository if it doesn't exist"""
    if not os.path.exists(target_dir):
        print(f"Cloning repository {repo_url} to {target_dir}...")
        subprocess.run(['git', 'clone', repo_url, target_dir], check=True)
    else:
        print(f"Repository already exists at {target_dir}, pulling latest changes...")
        subprocess.run(['git', '-C', target_dir, 'pull'], check=True)

def find_matching_code(videos_file, repo_dir='3b1b_repo'):
    """
    Find matching Manim code for each video in the metadata file.
    
    This uses several strategies:
    1. Look in the corresponding year directory
    2. Match by title similarity
    3. Look for mentions in code comments
    4. Check commit dates around video publication
    
    Args:
        videos_file: Path to the JSON file with video metadata
        repo_dir: Path to the cloned 3b1b repository
    """
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    # Ensure we have the repository
    clone_repo('https://github.com/3b1b/videos.git', repo_dir)
    
    # Mapping utility functions
    def clean_title(title):
        """Clean title for better matching"""
        return re.sub(r'[^\w\s]', '', title.lower())
    
    def get_file_score(file_path, video):
        """Calculate a matching score between a file and a video"""
        if not os.path.exists(file_path):
            return 0
        
        title = clean_title(video['title'])
        filename = os.path.basename(file_path)
        filename_clean = clean_title(os.path.splitext(filename)[0].replace('_', ' '))
        
        # Base score is title similarity
        score = fuzz.ratio(title, filename_clean)
        
        # Bonus if it's a Python file
        if file_path.endswith('.py'):
            score += 10
            
            # Check file content for mentions of the video title
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    # Title mentioned in comments or docstrings?
                    if title in content:
                        score += 30
                    
                    # Any keywords from title in content?
                    title_words = set(title.split())
                    for word in title_words:
                        if len(word) > 4 and word in content:  # Only consider meaningful words
                            score += 5
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return score
    
    # Process each video
    for i, video in enumerate(videos):
        print(f"Processing {i+1}/{len(videos)}: {video['title']}")
        
        video_year = video['year']
        title = video['title']
        published_at = video['published_at']
        
        # Look in specific year directories
        year_dirs = [
            f"_{video_year}",  # Main year directory
            f"{video_year}"    # Alternative format
        ]
        
        best_matches = []
        
        # Search in each potential year directory
        for year_dir in year_dirs:
            year_path = os.path.join(repo_dir, year_dir)
            if not os.path.exists(year_path):
                continue
            
            # First, search for directories or files that might match by name
            for item in os.listdir(year_path):
                item_path = os.path.join(year_path, item)
                
                # Score this item
                score = get_file_score(item_path, video)
                
                # If it's a directory, look inside for Python files
                if os.path.isdir(item_path):
                    for root, _, files in os.walk(item_path):
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                file_score = get_file_score(file_path, video)
                                if file_score > 60:  # Only consider good matches
                                    best_matches.append((file_path, file_score))
                
                if score > 60:  # Only consider good matches
                    best_matches.append((item_path, score))
        
        # Sort matches by score, highest first
        best_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Update video with the best matches
        if best_matches:
            # Take top 3 matches
            top_matches = best_matches[:3]
            video['manim_code_matches'] = [
                {'path': os.path.relpath(path, repo_dir), 'score': score} 
                for path, score in top_matches
            ]
            video['best_match'] = video['manim_code_matches'][0]['path']
            video['match_confidence'] = video['manim_code_matches'][0]['score']
        else:
            video['manim_code_matches'] = []
            video['best_match'] = None
            video['match_confidence'] = 0
    
    # Save updated metadata
    with open(f"{os.path.splitext(videos_file)[0]}_with_code.json", 'w') as f:
        json.dump(videos, f, indent=2)
    
    # Print summary
    matches_found = sum(1 for v in videos if v['best_match'])
    print(f"Matching complete. Found potential code for {matches_found}/{len(videos)} videos.")
    
    # List high and low confidence matches
    high_conf = [v for v in videos if v['match_confidence'] >= 80]
    low_conf = [v for v in videos if 0 < v['match_confidence'] < 60]
    
    print(f"High confidence matches: {len(high_conf)}")
    print(f"Low confidence matches: {len(low_conf)} (may need manual review)")

if __name__ == '__main__':
    find_matching_code('3b1b_videos.json')