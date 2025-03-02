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
            
            # Process all matches
            for match in video.get('manim_code_matches', []):
                src_path = os.path.join(repo_dir, match['path'])
                
                if os.path.exists(src_path):
                    if os.path.isdir(src_path):
                        # Copy directory contents
                        for item in os.listdir(src_path):
                            s = os.path.join(src_path, item)
                            d = os.path.join(code_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                    else:
                        # Copy single file
                        dst_file = os.path.join(code_dir, os.path.basename(src_path))
                        shutil.copy2(src_path, dst_file)
                else:
                    print(f"Warning: Source path not found: {src_path}")
        
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
        '3b1b_videos_with_code.json', 
        'transcripts', 
        '3b1b_repo'
    )