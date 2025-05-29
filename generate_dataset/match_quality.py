#!/usr/bin/env python3
"""
Analyze the quality and types of code matches in the 3Blue1Brown dataset.
Usage: python match_quality.py [dataset_path]
"""

import json
import os
import sys
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

def analyze_match_quality(dataset_path='3b1b_dataset/index.json'):
    """Analyze the quality of code matches in the dataset"""
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file not found at {dataset_path}")
        return
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    matched_videos = [v for v in videos if v.get('has_code', False)]
    
    if not matched_videos:
        print("No matched videos found in dataset")
        return
    
    print(f"Analyzing {len(matched_videos)} matched videos out of {len(videos)} total videos\n")
    
    # 1. Confidence score distribution
    confidence_scores = [v.get('match_confidence', 0) for v in matched_videos]
    
    # Calculate statistics
    avg_confidence = sum(confidence_scores) / len(confidence_scores)
    min_confidence = min(confidence_scores)
    max_confidence = max(confidence_scores)
    
    # Group by confidence range
    very_high = sum(1 for s in confidence_scores if s >= 100)
    high = sum(1 for s in confidence_scores if 80 <= s < 100)
    medium = sum(1 for s in confidence_scores if 60 <= s < 80)
    low = sum(1 for s in confidence_scores if s < 60)
    
    print("=== Confidence Score Analysis ===")
    print(f"Average confidence: {avg_confidence:.2f}")
    print(f"Minimum confidence: {min_confidence}")
    print(f"Maximum confidence: {max_confidence}")
    print(f"Very high confidence (≥100): {very_high} videos ({very_high/len(matched_videos)*100:.1f}%)")
    print(f"High confidence (80-99): {high} videos ({high/len(matched_videos)*100:.1f}%)")
    print(f"Medium confidence (60-79): {medium} videos ({medium/len(matched_videos)*100:.1f}%)")
    print(f"Low confidence (<60): {low} videos ({low/len(matched_videos)*100:.1f}%)")
    
    # 2. Directory vs File analysis
    match_types = [v.get('match_type', 'unknown') for v in matched_videos]
    type_counts = Counter(match_types)
    
    print("\n=== Directory vs File Analysis ===")
    for match_type, count in type_counts.items():
        print(f"{match_type}: {count} videos ({count/len(matched_videos)*100:.1f}%)")
    
    # 3. Match path analysis
    print("\n=== Match Path Analysis ===")
    
    # Extract year from paths
    year_pattern = r'[_]?(\d{4})'
    path_years = []
    for v in matched_videos:
        path = v.get('best_match', '')
        if path.startswith('_20') or path.startswith('20'):
            year = path.split('/')[0].replace('_', '')
            path_years.append(year)
        else:
            path_years.append('unknown')
    
    year_counts = Counter(path_years)
    print("Match distribution by year directory:")
    for year, count in sorted(year_counts.items()):
        print(f"{year}: {count} videos ({count/len(matched_videos)*100:.1f}%)")
    
    # 4. Spot check some matches for verification
    print("\n=== Random Sample of Matches for Verification ===")
    import random
    random.seed(42)  # For reproducibility
    
    # Sample from each confidence category
    very_high_samples = [v for v in matched_videos if v.get('match_confidence', 0) >= 100]
    high_samples = [v for v in matched_videos if 80 <= v.get('match_confidence', 0) < 100]
    medium_samples = [v for v in matched_videos if 60 <= v.get('match_confidence', 0) < 80]
    low_samples = [v for v in matched_videos if v.get('match_confidence', 0) < 60]
    
    for category, samples, name in [
        (very_high_samples, 3, "VERY HIGH CONFIDENCE"),
        (high_samples, 3, "HIGH CONFIDENCE"),
        (medium_samples, 3, "MEDIUM CONFIDENCE"),
        (low_samples, 3, "LOW CONFIDENCE")
    ]:
        if category:
            print(f"\n--- {name} SAMPLES ---")
            sample_videos = random.sample(category, min(len(category), samples))
            for v in sample_videos:
                print(f"Video: {v['title']}")
                print(f"Match: {v.get('best_match', 'None')}")
                print(f"Confidence: {v.get('match_confidence', 0)}")
                print(f"Type: {v.get('match_type', 'unknown')}")
                print(f"URL: https://www.youtube.com/watch?v={v['video_id']}")
                print("")
    
    # Generate visualizations
    try:
        # 1. Confidence score histogram
        plt.figure(figsize=(12, 6))
        bins = range(0, max(confidence_scores) + 10, 10)
        plt.hist(confidence_scores, bins=bins, alpha=0.7)
        plt.xlabel('Confidence Score')
        plt.ylabel('Number of Videos')
        plt.title('Distribution of Match Confidence Scores')
        plt.axvline(x=avg_confidence, color='r', linestyle='--', label=f'Average ({avg_confidence:.2f})')
        plt.axvline(x=60, color='orange', linestyle='--', label='Medium Threshold')
        plt.axvline(x=80, color='green', linestyle='--', label='High Threshold')
        plt.axvline(x=100, color='blue', linestyle='--', label='Very High Threshold')
        plt.legend()
        plt.savefig('generate_dataset/confidence_distribution.png')
        print("Generated confidence_distribution.png")
        
        # 2. Directory vs File pie chart
        plt.figure(figsize=(8, 8))
        labels = list(type_counts.keys())
        sizes = list(type_counts.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Match Types: Directory vs File')
        plt.savefig('generate_dataset/match_types.png')
        print("Generated match_types.png")
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")

if __name__ == "__main__":
    # Use provided path or default
    path = sys.argv[1] if len(sys.argv) > 1 else '3b1b_dataset/index.json'
    analyze_match_quality(path)