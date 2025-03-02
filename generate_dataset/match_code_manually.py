import json
import os
import argparse
import webbrowser
import shutil
from datetime import datetime
import readline  # For better CLI input experience

def manual_code_matcher(dataset_dir='3b1b_dataset', repo_dir='3b1b_repo'):
    """
    Interactive tool to help manually match videos to code files
    
    Args:
        dataset_dir: Path to the dataset directory
        repo_dir: Path to the cloned repository
    """
    # Load the index
    index_path = os.path.join(dataset_dir, 'index.json')
    if not os.path.exists(index_path):
        print(f"Error: Dataset index not found at {index_path}")
        return
    
    with open(index_path, 'r') as f:
        dataset = json.load(f)
    
    # Get unmatched videos
    unmatched = [v for v in dataset['videos'] if not v.get('has_code', False)]
    if not unmatched:
        print("All videos have been matched! Nothing to do.")
        return
    
    print(f"Found {len(unmatched)} unmatched videos.")
    
    # Check repository
    if not os.path.exists(repo_dir):
        print(f"Error: Repository directory not found at {repo_dir}")
        return
    
    # Get available years in the repo
    year_dirs = []
    for item in os.listdir(repo_dir):
        if os.path.isdir(os.path.join(repo_dir, item)) and (item.startswith('_') or item.isdigit()):
            year = item[1:] if item.startswith('_') else item
            if year.isdigit():
                year_dirs.append(item)
    
    if not year_dirs:
        print("Error: No year directories found in the repository.")
        return
    
    print("\nAvailable year directories in the repository:")
    for d in sorted(year_dirs):
        print(f"  - {d}")
    
    # Save backup of the index
    backup_path = f"{index_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(index_path, backup_path)
    print(f"\nBackup of index saved to {backup_path}")
    
    # Interactive matching
    matches_made = 0
    try:
        for i, video in enumerate(unmatched):
            video_id = video['video_id']
            title = video['title']
            year = video['year']
            
            print("\n" + "="*80)
            print(f"Video {i+1}/{len(unmatched)}: {title} ({year})")
            print(f"YouTube URL: https://www.youtube.com/watch?v={video_id}")
            
            # Try to open the matching year directory
            potential_year_dirs = [
                d for d in year_dirs 
                if (d.startswith('_') and d[1:] == str(year)) or d == str(year)
            ]
            
            if not potential_year_dirs:
                print(f"No matching year directory found for {year}.")
                potential_year_dirs = [
                    d for d in year_dirs
                    if (d.startswith('_') and d[1:] in [str(year-1), str(year+1)]) 
                    or d in [str(year-1), str(year+1)]
                ]
                if potential_year_dirs:
                    print(f"Suggesting nearby years: {', '.join(potential_year_dirs)}")
            
            # Options menu
            print("\nOptions:")
            print("  1. Open YouTube video")
            print("  2. Browse repository")
            print("  3. Enter code path manually")
            print("  4. Skip this video")
            print("  5. Quit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                # Open YouTube video
                url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Opening {url} in your browser...")
                webbrowser.open(url)
                input("Press Enter to continue...")
                continue
            
            elif choice == '2':
                # Browse repository
                if potential_year_dirs:
                    print("\nPotential year directories:")
                    for i, d in enumerate(potential_year_dirs):
                        print(f"  {i+1}. {d}")
                    
                    dir_choice = input("\nSelect a directory (number) or enter another directory name: ").strip()
                    
                    if dir_choice.isdigit() and 1 <= int(dir_choice) <= len(potential_year_dirs):
                        selected_dir = potential_year_dirs[int(dir_choice) - 1]
                    else:
                        selected_dir = dir_choice
                    
                    browse_path = os.path.join(repo_dir, selected_dir)
                    
                    if os.path.exists(browse_path) and os.path.isdir(browse_path):
                        print(f"\nBrowsing {browse_path}:")
                        items = sorted(os.listdir(browse_path))
                        
                        # Filter to show most relevant items first
                        # Split by type and sort directories first
                        dirs = [item for item in items if os.path.isdir(os.path.join(browse_path, item))]
                        files = [item for item in items if os.path.isfile(os.path.join(browse_path, item)) and item.endswith('.py')]
                        other_files = [item for item in items if item not in dirs and item not in files]
                        
                        all_items = dirs + files + other_files
                        
                        # Paginate if many items
                        page_size = 20
                        total_pages = (len(all_items) + page_size - 1) // page_size
                        current_page = 1
                        
                        while True:
                            start_idx = (current_page - 1) * page_size
                            end_idx = min(start_idx + page_size, len(all_items))
                            
                            print(f"\nPage {current_page}/{total_pages}:")
                            for i, item in enumerate(all_items[start_idx:end_idx], start=start_idx+1):
                                item_path = os.path.join(browse_path, item)
                                is_dir = os.path.isdir(item_path)
                                print(f"  {i}. {'[DIR] ' if is_dir else ''}{item}")
                            
                            nav = input("\nEnter item number to select, 'n' for next page, 'p' for previous, or 'q' to go back: ").strip()
                            
                            if nav == 'n' and current_page < total_pages:
                                current_page += 1
                            elif nav == 'p' and current_page > 1:
                                current_page -= 1
                            elif nav == 'q':
                                break
                            elif nav.isdigit() and 1 <= int(nav) <= len(all_items):
                                selected_item = all_items[int(nav) - 1]
                                selected_path = os.path.join(browse_path, selected_item)
                                
                                if os.path.isdir(selected_path):
                                    # Recurse into directory
                                    browse_path = selected_path
                                    all_items = sorted(os.listdir(browse_path))
                                    current_page = 1
                                    total_pages = (len(all_items) + page_size - 1) // page_size
                                else:
                                    # Select this file
                                    rel_path = os.path.relpath(selected_path, repo_dir)
                                    if input(f"Use '{rel_path}' as the match? (y/n): ").strip().lower() == 'y':
                                        # Save the match
                                        add_match_to_dataset(dataset, video, rel_path, repo_dir, dataset_dir)
                                        matches_made += 1
                                        break
                    else:
                        print(f"Directory {browse_path} not found.")
                        input("Press Enter to continue...")
                else:
                    print("No potential year directories found.")
                    input("Press Enter to continue...")
            
            elif choice == '3':
                # Manual path entry
                print("\nEnter the path to the code file or directory, relative to repository root.")
                print("Examples: '_2018/fourier/main.py' or '_2018/fourier'")
                
                path = input("Path: ").strip()
                full_path = os.path.join(repo_dir, path)
                
                if os.path.exists(full_path):
                    if input(f"Use '{path}' as the match? (y/n): ").strip().lower() == 'y':
                        # Save the match
                        add_match_to_dataset(dataset, video, path, repo_dir, dataset_dir)
                        matches_made += 1
                else:
                    print(f"Error: Path {full_path} does not exist.")
                    input("Press Enter to continue...")
            
            elif choice == '4':
                # Skip
                print(f"Skipping video: {title}")
                continue
            
            elif choice == '5':
                # Quit
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\nManual matching interrupted.")
    
    # Save changes
    if matches_made > 0:
        with open(index_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"\nSaved {matches_made} new matches to the dataset index.")
    else:
        print("\nNo new matches were made.")

def add_match_to_dataset(dataset, video, path, repo_dir, dataset_dir):
    """Add a manual match to the dataset"""
    video_id = video['video_id']
    
    # Update video record in the index
    for v in dataset['videos']:
        if v['video_id'] == video_id:
            v['has_code'] = True
            v['best_match'] = path
            v['match_type'] = 'directory' if os.path.isdir(os.path.join(repo_dir, path)) else 'file'
            v['match_confidence'] = 100  # Manual match has high confidence
            v['manually_matched'] = True
            break
    
    # Update dataset counts
    dataset['videos_with_code'] = sum(1 for v in dataset['videos'] if v.get('has_code', False))
    
    # Create the code directory in the dataset
    video_dir = os.path.join(dataset_dir, video_id)
    code_dir = os.path.join(video_dir, 'code')
    os.makedirs(code_dir, exist_ok=True)
    
    # Create README
    with open(os.path.join(code_dir, 'README.md'), 'w') as f:
        f.write(f"# Code for: {video['title']}\n\n")
        f.write(f"- Match confidence: 100 (manually matched)\n")
        f.write(f"- Match type: {v['match_type']}\n")
        f.write(f"- Path: {path}\n")
    
    # Copy the code
    src_path = os.path.join(repo_dir, path)
    if os.path.isdir(src_path):
        # Copy directory contents
        print(f"Copying directory: {src_path}")
        for item in os.listdir(src_path):
            s = os.path.join(src_path, item)
            d = os.path.join(code_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    else:
        # Copy single file
        print(f"Copying file: {src_path}")
        dst_file = os.path.join(code_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_file)
    
    print(f"Successfully matched and copied code for video: {video['title']}")

def main():
    parser = argparse.ArgumentParser(description='Manually match 3Blue1Brown videos to code files')
    parser.add_argument('--dataset', default='3b1b_dataset', help='Path to the dataset directory')
    parser.add_argument('--repo', default='3b1b_repo', help='Path to the repository directory')
    
    args = parser.parse_args()
    manual_code_matcher(args.dataset, args.repo)

if __name__ == '__main__':
    main()