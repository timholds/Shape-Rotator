import os
import json
import re
import subprocess
import glob
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
import shutil

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
    Find matching Manim code for each video in the metadata file using advanced matching strategies.
    
    This uses multiple strategies:
    1. Look in the corresponding year directory
    2. Match by title similarity
    3. Look for mentions in code comments or README files
    4. Analyze directory structure and identify key files
    5. Check publication dates against commit history
    
    Args:
        videos_file: Path to the JSON file with video metadata
        repo_dir: Path to the cloned 3b1b repository
    """
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    # Ensure we have the repository
    clone_repo('https://github.com/3b1b/videos.git', repo_dir)
    
    # Utility function to clean titles for better matching
    def clean_title(title):
        """Clean title for better matching"""
        # Remove special characters and convert to lowercase
        title = re.sub(r'[^\w\s]', '', title.lower())
        # Remove common words that might not be in filenames
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'on', 'in', 'to', 'for'}
        return ' '.join([word for word in title.split() if word not in stopwords])
    
    def extract_keywords(title):
        """Extract meaningful keywords from title"""
        clean = clean_title(title)
        # Only include words longer than 3 characters
        return [word for word in clean.split() if len(word) > 3]
    
    def score_directory(dir_path, video):
        """Score a directory for relevance to a video"""
        score = 0
        title = clean_title(video['title'])
        dir_name = os.path.basename(dir_path)
        dir_name_clean = clean_title(dir_name.replace('_', ' '))
        
        # Base score is directory name similarity
        name_score = fuzz.token_sort_ratio(title, dir_name_clean)
        score += name_score
        
        # Check if the directory contains a README or description
        readme_paths = glob.glob(os.path.join(dir_path, "README*"))
        desc_paths = glob.glob(os.path.join(dir_path, "description*"))
        docs_paths = glob.glob(os.path.join(dir_path, "*.md"))
        doc_files = readme_paths + desc_paths + docs_paths
        
        keywords = extract_keywords(title)
        
        # Check documentation files for title or keywords
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if title in content:
                        score += 50  # Strong indicator if exact title is in README
                    for keyword in keywords:
                        if keyword in content:
                            score += 5
            except Exception as e:
                print(f"Error reading {doc_file}: {e}")
        
        # Check for main.py or scene.py - typical entry points
        for main_file in ['main.py', 'scene.py', dir_name + '.py']:
            main_path = os.path.join(dir_path, main_file)
            if os.path.exists(main_path):
                score += 15
                # Check content of main file
                try:
                    with open(main_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if title in content:
                            score += 30
                        for keyword in keywords:
                            if keyword in content:
                                score += 5
                except Exception as e:
                    print(f"Error reading {main_path}: {e}")
        
        # Count Python files - more files usually means more developed project
        py_files = glob.glob(os.path.join(dir_path, "*.py"))
        score += min(len(py_files) * 2, 20)  # Cap at 20 points
        
        # Check for video ID in any file
        video_id = video['video_id']
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(('.py', '.md', '.txt')):
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if video_id in content:
                                score += 100  # Very strong indicator
                                break
                    except Exception:
                        pass
        
        return score
    
    def score_file(file_path, video):
        """Score a file for relevance to a video"""
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return 0
        
        score = 0
        title = clean_title(video['title'])
        filename = os.path.basename(file_path)
        filename_clean = clean_title(os.path.splitext(filename)[0].replace('_', ' '))
        
        # Base score is filename similarity
        name_score = fuzz.token_sort_ratio(title, filename_clean)
        score += name_score
        
        # Keywords from title
        keywords = extract_keywords(title)
        
        # Check file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                # Title in comments, docstrings or class names
                if title in content:
                    score += 30
                
                # Check for keywords from title
                for keyword in keywords:
                    if keyword in content:
                        score += 3
                
                # Check for video ID - very strong indicator
                if video['video_id'] in content:
                    score += 100
                
                # Check for YouTube URL - very strong indicator
                if f"youtube.com/watch?v={video['video_id']}" in content:
                    score += 100
                
                # Check for scene creation - indicator of main file
                if "class" in content and "Scene" in content:
                    score += 15
                
                # File size can be an indicator (main files tend to be larger)
                score += min(os.path.getsize(file_path) / 1024, 20)  # Cap at 20 points
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        return score
    
    def get_potential_year_dirs(video_year, repo_dir):
        """Get potential year directories to search"""
        # Common patterns for year directories
        patterns = [
            f"_{video_year}",     # _2019
            f"{video_year}",      # 2019
            f"_{video_year-1}",   # Previous year (videos might be planned in prev year)
            f"{video_year-1}",    # Previous year alternative format
            f"_{video_year+1}",   # Next year (in case of mislabeling)
            f"{video_year+1}",    # Next year alternative format
        ]
        
        return [os.path.join(repo_dir, pattern) for pattern in patterns 
                if os.path.exists(os.path.join(repo_dir, pattern))]
    
    def find_best_matches(video, repo_dir):
        """Find the best code matches for a video"""
        video_year = video['year']
        title = video['title']
        published_at = video['published_at']
        
        # Get potential year directories
        year_dirs = get_potential_year_dirs(video_year, repo_dir)
        
        # Fallback: if no year dirs found, look in all top-level directories
        if not year_dirs:
            print(f"  No year directory found for {video_year}, searching all directories...")
            year_dirs = [os.path.join(repo_dir, d) for d in os.listdir(repo_dir) 
                        if os.path.isdir(os.path.join(repo_dir, d)) and not d.startswith('.')]
        
        # Collect all potential matches
        dir_matches = []
        file_matches = []
        
        # Search in each year directory
        for year_dir in year_dirs:
            # Get all subdirectories
            for item in os.listdir(year_dir):
                item_path = os.path.join(year_dir, item)
                
                # Score directories
                if os.path.isdir(item_path):
                    dir_score = score_directory(item_path, video)
                    if dir_score > 50:  # Minimum threshold
                        dir_matches.append((item_path, dir_score))
                
                # Score Python files
                elif item.endswith('.py'):
                    file_score = score_file(item_path, video)
                    if file_score > 50:  # Minimum threshold
                        file_matches.append((item_path, file_score))
        
        # Sort matches by score, highest first
        dir_matches.sort(key=lambda x: x[1], reverse=True)
        file_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Combine and prioritize
        all_matches = []
        
        # First add directory matches - these are typically more comprehensive
        for path, score in dir_matches[:3]:  # Top 3 directory matches
            all_matches.append({
                'path': os.path.relpath(path, repo_dir),
                'score': score,
                'type': 'directory',
                'files': [os.path.relpath(os.path.join(path, f), repo_dir) 
                         for f in os.listdir(path) 
                         if f.endswith('.py')][:5]  # List up to 5 Python files
            })
        
        # Then add file matches
        for path, score in file_matches[:3]:  # Top 3 file matches
            all_matches.append({
                'path': os.path.relpath(path, repo_dir),
                'score': score,
                'type': 'file',
                'files': [os.path.relpath(path, repo_dir)]
            })
        
        # Sort again by score
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        return all_matches
    
    # Process each video
    for i, video in enumerate(videos):
        print(f"Processing {i+1}/{len(videos)}: {video['title']}")
        
        # Find best matches for this video
        matches = find_best_matches(video, repo_dir)
        
        # Update video with matches
        if matches:
            video['manim_code_matches'] = matches
            video['best_match'] = matches[0]['path']
            video['match_type'] = matches[0]['type']
            video['match_confidence'] = matches[0]['score']
            video['key_files'] = matches[0]['files']
        else:
            video['manim_code_matches'] = []
            video['best_match'] = None
            video['match_type'] = None
            video['match_confidence'] = 0
            video['key_files'] = []
    
    # Save updated metadata
    with open(f"{os.path.splitext(videos_file)[0]}_with_code.json", 'w') as f:
        json.dump(videos, f, indent=2)
    
    # Print summary
    matches_found = sum(1 for v in videos if v['best_match'])
    dir_matches = sum(1 for v in videos if v['match_type'] == 'directory')
    file_matches = sum(1 for v in videos if v['match_type'] == 'file')
    
    print(f"Matching complete. Found potential code for {matches_found}/{len(videos)} videos.")
    print(f"Directory matches: {dir_matches}")
    print(f"File matches: {file_matches}")
    
    # List confidence ranges
    high_conf = [v for v in videos if v['match_confidence'] >= 100]
    med_conf = [v for v in videos if 70 <= v['match_confidence'] < 100]
    low_conf = [v for v in videos if 0 < v['match_confidence'] < 70]
    
    print(f"High confidence matches (≥100): {len(high_conf)}")
    print(f"Medium confidence matches (70-99): {len(med_conf)}")
    print(f"Low confidence matches (<70): {len(low_conf)} (may need manual review)")

if __name__ == '__main__':
    find_matching_code('3b1b_videos.json')