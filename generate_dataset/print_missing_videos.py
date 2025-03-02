#!/usr/bin/env python3
"""
Simple script to print videos that don't have matching code.
Usage: python print_missing.py [dataset_path]
"""

import json
import sys
import os

def print_missing_videos(dataset_path='3b1b_dataset/index.json'):
    """Print all videos that don't have matching code files"""
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file not found at {dataset_path}")
        return
    
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON file at {dataset_path}")
        return
    
    videos = data.get('videos', [])
    if not videos:
        print("No videos found in dataset")
        return
    
    # Find unmatched videos
    unmatched = [v for v in videos if not v.get('has_code', False)]
    
    if not unmatched:
        print("All videos have matching code!")
        return
    
    # Group by year
    by_year = {}
    for v in unmatched:
        year = v.get('year', 'Unknown')
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(v)
    
    # Print summary
    print(f"Found {len(unmatched)} videos without matching code out of {len(videos)} total videos")
    print("\n=== Videos Missing Code By Year ===")
    
    # Print by year
    for year in sorted(by_year.keys()):
        year_videos = by_year[year]
        print(f"\n== {year} ({len(year_videos)} videos) ==")
        
        for i, v in enumerate(year_videos):
            print(f"{i+1}. {v['title']}")
            print(f"   URL: https://www.youtube.com/watch?v={v['video_id']}")
            print("")

if __name__ == "__main__":
    # Use provided path or default
    path = sys.argv[1] if len(sys.argv) > 1 else '3b1b_dataset/index.json'
    print_missing_videos(path)