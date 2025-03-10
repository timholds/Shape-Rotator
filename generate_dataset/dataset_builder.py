import os
import json
import shutil

def build_dataset(videos_file, transcript_dir, repo_dir, output_dir='3b1b_dataset'):
    """
    Build the final dataset structure with transcripts and code.
    
    Args:
        videos_file: Path to the JSON file with video metadata and code matches
        transcript_dir: Directory containing the downloaded transcripts
        repo_dir: Path to the cloned 3b1b repository
        output_dir: Directory to save the final dataset
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    # Create dataset index file
    dataset_index = {
        'total_videos': len(videos),
        'videos_with_transcripts': sum(1 for v in videos if v.get('has_transcript', False)),
        'videos_with_code': sum(1 for v in videos if v.get('best_match')),
        'dataset_creation_date': os.path.basename(__file__),
        'videos': []
    }
    
    # Process each video
    for video in videos:
        video_id = video['video_id']
        title = video['title']
        
        # Create directory for this video
        video_dir = os.path.join(output_dir, video_id)
        os.makedirs(video_dir, exist_ok=True)
        
        # Save video metadata
        with open(os.path.join(video_dir, 'metadata.json'), 'w') as f:
            json.dump(video, f, indent=2)
        
        # Copy transcripts if available
        if video.get('has_transcript', False):
            for suffix in ['_clean', '_timestamped']:
                src = os.path.join(transcript_dir, f"{video_id}{suffix}.txt")
                if os.path.exists(src):
                    dst = os.path.join(video_dir, f"transcript{suffix}.txt")
                    shutil.copy(src, dst)
        
        # Copy code files if available
        if video.get('best_match'):
            code_dir = os.path.join(video_dir, 'code')
            os.makedirs(code_dir, exist_ok=True)
            
            # Process best match
            best_match = video.get('manim_code_matches', [])[0] if video.get('manim_code_matches') else None
            if best_match:
                match_type = best_match.get('type')
                src_path = os.path.join(repo_dir, best_match['path'])
                
                # Create a README with match information
                with open(os.path.join(code_dir, 'README.md'), 'w') as f:
                    f.write(f"# Code for: {video['title']}\n\n")
                    f.write(f"- Match confidence: {best_match['score']}/100\n")
                    f.write(f"- Match type: {match_type}\n")
                    f.write(f"- Path: {best_match['path']}\n")
                    if match_type == 'directory':
                        f.write(f"- Key files:\n")
                        for file in best_match.get('files', []):
                            f.write(f"  - {file}\n")
                
                if os.path.exists(src_path):
                    if match_type == 'directory':
                        # Copy directory contents
                        print(f"  Copying directory: {src_path}")
                        
                        # First, copy the important Python files
                        for file_path in best_match.get('files', []):
                            full_src = os.path.join(repo_dir, file_path)
                            if os.path.exists(full_src):
                                # Create subdirectories if needed
                                rel_path = os.path.relpath(full_src, src_path)
                                dst_file = os.path.join(code_dir, rel_path)
                                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                                
                                # Copy the file
                                shutil.copy2(full_src, dst_file)
                                print(f"    Copied: {rel_path}")
                        
                        # Now copy other relevant files (README, etc.)
                        for item in os.listdir(src_path):
                            s = os.path.join(src_path, item)
                            d = os.path.join(code_dir, item)
                            
                            # Skip Python files (already copied) and large directories
                            if item.endswith('.py') or (os.path.isdir(s) and item in ['__pycache__']):
                                continue
                                
                            if os.path.isdir(s):
                                try:
                                    shutil.copytree(s, d, dirs_exist_ok=True)
                                    print(f"    Copied directory: {item}")
                                except Exception as e:
                                    print(f"    Error copying directory {item}: {e}")
                            else:
                                try:
                                    shutil.copy2(s, d)
                                    print(f"    Copied file: {item}")
                                except Exception as e:
                                    print(f"    Error copying file {item}: {e}")
                    else:
                        # Copy single file
                        print(f"  Copying file: {src_path}")
                        dst_file = os.path.join(code_dir, os.path.basename(src_path))
                        shutil.copy2(src_path, dst_file)
                else:
                    print(f"  Warning: Source path not found: {src_path}")
            
            # Add a simple script to run the code (if it's a directory with Python files)
            if match_type == 'directory' and best_match.get('files'):
                with open(os.path.join(code_dir, 'run_manim.py'), 'w') as f:
                    f.write("""#!/usr/bin/env python3
# Helper script to run the Manim code

import os
import sys
import importlib.util
import subprocess

def main():
    print("Manim Runner for 3Blue1Brown Videos")
    print("===================================")
    
    # Check if manim is installed
    try:
        import manim
        print("Manim found:", manim.__version__)
    except ImportError:
        print("Manim not found. Please install it with:")
        print("pip install manim")
        return
    
    # List Python files in this directory
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != os.path.basename(__file__)]
    
    if not py_files:
        print("No Python files found in this directory.")
        return
    
    print("\\nAvailable files:")
    for i, file in enumerate(py_files):
        print(f"{i+1}. {file}")
    
    try:
        choice = int(input("\\nSelect a file to run (number): ")) - 1
        if choice < 0 or choice >= len(py_files):
            print("Invalid selection.")
            return
        
        selected_file = py_files[choice]
        print(f"\\nRunning: {selected_file}")
        
        # Find manim scenes in the file
        spec = importlib.util.spec_from_file_location("module", selected_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        scenes = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr.__module__ == "module" and "Scene" in str(attr.__bases__):
                scenes.append(attr_name)
        
        if not scenes:
            print("No manim scenes found in this file.")
            return
        
        print("\\nAvailable scenes:")
        for i, scene in enumerate(scenes):
            print(f"{i+1}. {scene}")
        
        scene_choice = int(input("\\nSelect a scene to render (number): ")) - 1
        if scene_choice < 0 or scene_choice >= len(scenes):
            print("Invalid selection.")
            return
        
        selected_scene = scenes[scene_choice]
        
        # Run manim
        cmd = ["manim", selected_file, selected_scene, "-p"]
        print(f"\\nRunning command: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
""")
        
        # Add to dataset index
        dataset_index['videos'].append({
            'video_id': video_id,
            'url': video['url'],
            'title': title,
            'year': video['year'],
            'has_transcript': video.get('has_transcript', False),
            'has_code': bool(video.get('best_match')),
            'match_confidence': video.get('match_confidence', 0)
        })
    
    # Save dataset index
    with open(os.path.join(output_dir, 'index.json'), 'w') as f:
        json.dump(dataset_index, f, indent=2)
    
    print(f"Dataset creation complete! Saved to {output_dir}")
    print(f"Total videos: {dataset_index['total_videos']}")
    print(f"Videos with transcripts: {dataset_index['videos_with_transcripts']}")
    print(f"Videos with code: {dataset_index['videos_with_code']}")

if __name__ == '__main__':
    build_dataset(
        'generate_dataset/3b1b_videos_with_code.json', 
        'generate_dataset/transcripts', 
        'generate_dataset/3b1b_repo'
    )