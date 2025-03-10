import os
import argparse
from dotenv import load_dotenv
from get_youtube_videos import get_all_3b1b_videos, save_video_metadata
from get_youtube_transcripts import download_transcripts
from match_code_to_videos import find_matching_code
from dataset_builder import build_dataset
from analyze_missing_code import analyze_missing_matches
from match_code_manually import manual_code_matcher

# Load environment variables from .env.development
load_dotenv('.env.development')

def main():
    parser = argparse.ArgumentParser(description='Build a dataset of 3Blue1Brown videos with transcripts and Manim code')
    parser.add_argument('--skip-videos', action='store_true', help='Skip downloading video metadata')
    parser.add_argument('--skip-transcripts', action='store_true', help='Skip downloading transcripts')
    parser.add_argument('--skip-code-matching', action='store_true', help='Skip matching videos to code')
    parser.add_argument('--output-dir', default='generate_dataset/3b1b_dataset', help='Output directory for the dataset')
    parser.add_argument('--analyze', action='store_true', help='Run analysis on missing code matches')
    parser.add_argument('--manual-match', action='store_true', help='Run interactive tool to manually match videos to code')
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs('transcripts', exist_ok=True)
    
    # Step 1: Collect YouTube video data
    if not args.skip_videos:
        print("\n=== Step 1: Collecting 3Blue1Brown video metadata ===")
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            print("No YouTube API key found in .env.development")
            api_key = input("Enter your YouTube API key: ")
        
        videos = get_all_3b1b_videos(api_key)
        save_video_metadata(videos)
    
    # Step 2: Download transcripts
    if not args.skip_transcripts:
        print("\n=== Step 2: Downloading video transcripts ===")
        download_transcripts('generate_dataset/3b1b_videos.json')
    
    # Step 3: Match videos to code
    if not args.skip_code_matching:
        print("\n=== Step 3: Matching videos to Manim code ===")
        find_matching_code('generate_dataset/3b1b_videos.json')
    
    # Step 4: Build the dataset
    print("\n=== Step 4: Building the final dataset ===")
    build_dataset(
        'generate_dataset/3b1b_videos_with_code.json',
        'generate_dataset/transcripts',
        'generate_dataset/3b1b_repo',
        args.output_dir
    )
    
    print("\n=== Dataset creation complete! ===")
    print(f"Dataset is available in the '{args.output_dir}' directory.")
    
    # Optional analysis of missing matches
    if args.analyze:
        print("\n=== Step 5: Analyzing missing code matches ===")
        analyze_missing_matches(os.path.join(args.output_dir, 'index.json'))
    
    # Optional manual matching
    if args.manual_match:
        print("\n=== Step 6: Manual code matching ===")
        manual_code_matcher(args.output_dir, '3b1b_repo')
    
    print("\nNOTE: This dataset only contains:")
    print("- Video metadata (titles, descriptions, dates)")
    print("- Video transcripts (text only, not the actual videos)")
    print("- Corresponding Manim code files from the GitHub repository")
    print("\nThe actual video files are NOT downloaded. Total dataset size should")
    print("be relatively small (typically less than a few hundred MB).")

if __name__ == '__main__':
    main()