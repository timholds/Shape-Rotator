#!/usr/bin/env python3
"""
Run tools on the 3Blue1Brown dataset without recreating it.
Usage: python tools.py [command]

Commands:
  list-missing    - List videos without code matches
  analyze         - Run detailed analysis on missing matches
  manual-match    - Run interactive tool to manually match videos
"""

import os
import sys
import argparse
from analyze_missing_code import analyze_missing_matches
from match_code_manually import manual_code_matcher
from print_missing_videos import print_missing_videos

def main():
    parser = argparse.ArgumentParser(description='Tools for the 3Blue1Brown dataset')
    parser.add_argument('command', choices=['list-missing', 'analyze', 'manual-match'], 
                      help='Tool to run')
    parser.add_argument('--dataset', default='generate_dataset/3b1b_dataset', 
                      help='Path to dataset directory')
    
    args = parser.parse_args()
    
    dataset_dir = args.dataset
    index_path = os.path.join(dataset_dir, 'index.json')
    
    if not os.path.exists(index_path):
        print(f"Error: Dataset index not found at {index_path}")
        print("Please run main.py first to create the dataset.")
        return 1
    
    if args.command == 'list-missing':
        print_missing_videos(index_path)
    
    elif args.command == 'analyze':
        analyze_missing_matches(index_path)
    
    elif args.command == 'manual-match':
        manual_code_matcher(dataset_dir, 'generate_dataset/3b1b_repo')
    
    return 0

if __name__ == "__main__":
    sys.exit(main())