import os
import argparse
from get_youtube_videos import get_all_3b1b_videos, save_video_metadata
from get_youtube_transcripts import download_transcripts
from match_code_to_videos import find_matching_code
from dataset_builder import build_dataset
from dotenv import load_dotenv
load_dotenv('.env.development')

def main():
    parser = argparse.ArgumentParser(description='Build a dataset of 3Blue1Brown videos with transcripts and Manim code')
    parser.add_argument('--api-key', help='YouTube Data API key')
    parser.add_argument('--skip-videos', action='store_true', help='Skip downloading video metadata')
    parser.add_argument('--skip-transcripts', action='store_true', help='Skip downloading transcripts')
    parser.add_argument('--skip-code-matching', action='store_true', help='Skip matching videos to code')
    parser.add_argument('--output-dir', default='3b1b_dataset', help='Output directory for the dataset')
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs('transcripts', exist_ok=True)
    
    # Step 1: Collect YouTube video data
    if not args.skip_videos:
        print("\n=== Step 1: Collecting 3Blue1Brown video metadata ===")
        api_key = args.api_key or os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            print("Checking .env.development for YOUTUBE_API_KEY...")
            if not api_key:
                api_key = input("Enter your YouTube API key: ")
        
        videos = get_all_3b1b_videos(api_key)
        save_video_metadata(videos)
    
    # Step 2: Download transcripts
    if not args.skip_transcripts:
        print("\n=== Step 2: Downloading video transcripts ===")
        download_transcripts('3b1b_videos.json')
    
    # Step 3: Match videos to code
    if not args.skip_code_matching:
        print("\n=== Step 3: Matching videos to Manim code ===")
        find_matching_code('3b1b_videos.json')
    
    # Step 4: Build the dataset
    print("\n=== Step 4: Building the final dataset ===")
    build_dataset(
        '3b1b_videos_with_code.json',
        'transcripts',
        '3b1b_repo',
        args.output_dir
    )
    
    print("\n=== Dataset creation complete! ===")
    print(f"Dataset is available in the '{args.output_dir}' directory.")

if __name__ == '__main__':
    main()