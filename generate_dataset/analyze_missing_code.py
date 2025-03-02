import json
import os
import argparse
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def analyze_missing_matches(dataset_file, output_dir='analysis'):
    """
    Analyze videos that don't have code matches to identify patterns
    and potential issues with the matching algorithm.
    
    Args:
        dataset_file: Path to the dataset JSON file
        output_dir: Directory to save analysis results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the dataset
    with open(dataset_file, 'r') as f:
        data = json.load(f)
    
    videos = data['videos']
    
    # Separate matched and unmatched videos
    matched = [v for v in videos if v.get('has_code', False)]
    unmatched = [v for v in videos if not v.get('has_code', False)]
    
    print(f"Total videos: {len(videos)}")
    print(f"Matched videos: {len(matched)} ({len(matched)/len(videos)*100:.1f}%)")
    print(f"Unmatched videos: {len(unmatched)} ({len(unmatched)/len(videos)*100:.1f}%)")
    
    # Analyze unmatched videos
    if unmatched:
        print("\n===== ANALYSIS OF UNMATCHED VIDEOS =====")
        
        # 1. Check distribution by year
        years = [v.get('year') for v in unmatched]
        year_counts = Counter(years)
        print("\nDistribution by year:")
        for year in sorted(year_counts.keys()):
            total_year = sum(1 for v in videos if v.get('year') == year)
            print(f"  {year}: {year_counts[year]}/{total_year} videos unmatched ({year_counts[year]/total_year*100:.1f}%)")
        
        # Plot year distribution
        plt.figure(figsize=(12, 6))
        years_all = [v.get('year') for v in videos]
        years_all_count = Counter(years_all)
        
        x = sorted(years_all_count.keys())
        matched_counts = [years_all_count[year] - year_counts.get(year, 0) for year in x]
        unmatched_counts = [year_counts.get(year, 0) for year in x]
        
        plt.bar(x, matched_counts, label='Matched')
        plt.bar(x, unmatched_counts, bottom=matched_counts, label='Unmatched')
        plt.xlabel('Year')
        plt.ylabel('Number of Videos')
        plt.title('Video Distribution by Year')
        plt.legend()
        plt.savefig(os.path.join(output_dir, 'year_distribution.png'))
        
        # 2. Check for patterns in titles
        print("\nCommon words in unmatched video titles:")
        all_words = []
        for v in unmatched:
            words = v['title'].lower().split()
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        # Remove common English words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'on', 'in', 'to', 'for', 'of', 'with'}
        for word in stopwords:
            if word in word_counts:
                del word_counts[word]
        
        for word, count in word_counts.most_common(15):
            print(f"  {word}: {count} occurrences")
        
        # 3. List all unmatched videos
        print("\nUnmatched videos:")
        for i, v in enumerate(unmatched):
            print(f"  {i+1}. [{v.get('year')}] {v['title']}")
        
        # Save unmatched video details to file
        with open(os.path.join(output_dir, 'unmatched_videos.json'), 'w') as f:
            json.dump(unmatched, f, indent=2)
        
        # 4. Try with lower confidence threshold
        low_conf_matches = []
        if unmatched and 'manim_code_matches' in unmatched[0]:
            print("\nVideos that had potential matches but below threshold:")
            
            # Check for videos with low confidence matches
            for v in unmatched:
                matches = v.get('manim_code_matches', [])
                if matches:
                    best_match = max(matches, key=lambda m: m['score'])
                    low_conf_matches.append((v['title'], best_match['score'], best_match['path']))
            
            # Sort by score, highest first
            low_conf_matches.sort(key=lambda x: x[1], reverse=True)
            
            for title, score, path in low_conf_matches:
                print(f"  {title} (score: {score}) -> {path}")
            
            # Plot score distribution
            if low_conf_matches:
                scores = [m[1] for m in low_conf_matches]
                plt.figure(figsize=(10, 6))
                plt.hist(scores, bins=20, alpha=0.7)
                plt.axvline(x=50, color='r', linestyle='--', label='Current Threshold (50)')
                plt.xlabel('Match Score')
                plt.ylabel('Number of Videos')
                plt.title('Score Distribution of Unmatched Videos')
                plt.legend()
                plt.savefig(os.path.join(output_dir, 'score_distribution.png'))
                
                # Suggest new threshold
                potential_thresholds = range(10, 50, 5)
                for threshold in potential_thresholds:
                    additional_matches = sum(1 for s in scores if s >= threshold)
                    print(f"  With threshold {threshold}: {additional_matches} additional matches")
        
        # 5. Generate recommendations
        print("\nRECOMMENDATIONS:")
        
        if year_counts:
            max_year = max(year_counts.items(), key=lambda x: x[1])[0]
            print(f"1. Focus on {max_year} videos which have the most unmatched content.")
        
        if low_conf_matches:
            if any(score > 30 for _, score, _ in low_conf_matches):
                print("2. Consider lowering the confidence threshold to 30-40 for more matches (with manual verification).")
            
        print("3. For manual matching, start with these videos:")
        for i, v in enumerate(unmatched[:5]):
            print(f"   {i+1}. {v['title']}")

def main():
    parser = argparse.ArgumentParser(description='Analyze missing code matches in the 3Blue1Brown dataset')
    parser.add_argument('--dataset', default='3b1b_dataset/index.json', help='Path to the dataset index file')
    parser.add_argument('--output', default='analysis', help='Directory to save analysis results')
    
    args = parser.parse_args()
    analyze_missing_matches(args.dataset, args.output)

if __name__ == '__main__':
    main()