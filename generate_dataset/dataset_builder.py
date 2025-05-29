import os
import json
import shutil
import sys 


def concatenate_code_files(code_dir, output_file):
    """Concatenate all Python files in the code directory into a single file."""
    all_code = []
    
    # Find Python files
    py_files = []
    for root, _, files in os.walk(code_dir):
        for file in files:
            if file.endswith('.py') and file != 'run_manim.py':
                py_files.append(os.path.join(root, file))
    
    # Sort files to put main files first
    py_files.sort(key=lambda x: 0 if os.path.basename(x) in ['main.py', 'scene.py'] else 1)
    
    # Add header comment
    all_code.append(f"# Combined Manim code files from {os.path.basename(code_dir)}\n\n")
    
    # Concatenate files
    for py_file in py_files:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
        
        rel_path = os.path.relpath(py_file, code_dir)
        all_code.append(f"# ----- File: {rel_path} -----\n")
        all_code.append(file_content)
        all_code.append("\n\n")
    
    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(all_code))


def analyze_imports_and_consolidate(main_file_path, repo_dir, output_file_path):
    """
    Analyze a Python file for imports from the repo and create a consolidated file
    with all necessary code.
    
    Args:
        main_file_path: Path to the main Python file
        repo_dir: Path to the repository root
        output_file_path: Where to save the consolidated file
    """
    import ast
    import sys
    
    # Read the main file
    with open(main_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        main_code = f.read()
    
    # Parse the AST to find imports
    try:
        tree = ast.parse(main_code)
    except SyntaxError as e:
        print(f"  Error parsing {main_file_path}: {e}")
        # Just copy the file as-is instead of consolidating
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Original file with syntax error: {main_file_path}\n\n")
            f.write(main_code)
        return False
    
    # Track processed modules to avoid duplicates
    processed_modules = set()
    
    # Consolidated code with main file at the top
    consolidated_code = f"# Consolidated code for {os.path.basename(main_file_path)}\n"
    consolidated_code += f"# Original file: {main_file_path}\n\n"
    
    # Process imports separately, then add code
    import_sections = []
    
    # Define a function to process imports recursively
    def process_imports(file_path, depth=0):
        if depth > 5:  # Prevent infinite recursion
            return f"# Max import depth reached for {file_path}\n"
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            return f"# Failed to read {file_path}: {e}\n"
            
        file_dir = os.path.dirname(file_path)
        
        # Track this file's imports
        file_imports = []
        
        # Parse imports in this file
        try:
            tree = ast.parse(code)
            
            # Find all imports
            local_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name not in processed_modules:
                            local_imports.append((name.name, None))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in processed_modules:
                        for name in node.names:
                            local_imports.append((node.module, name.name))
            
            # Process found imports
            for module_name, item_name in local_imports:
                if module_name in processed_modules:
                    continue
                    
                # Skip standard library and installed packages
                if module_name in sys.modules or module_name.startswith(('manim', 'numpy', 'scipy', 'pygame')):
                    continue
                    
                # Try to find the module in the repository
                module_path = module_name.replace('.', '/')
                
                # Check possible locations
                potential_paths = [
                    os.path.join(file_dir, f"{module_path}.py"),
                    os.path.join(file_dir, module_path, "__init__.py"),
                    os.path.join(repo_dir, f"{module_path}.py"),
                    os.path.join(repo_dir, module_path, "__init__.py")
                ]
                
                found = False
                for p in potential_paths:
                    if os.path.exists(p):
                        processed_modules.add(module_name)
                        import_section = f"# Inlined import: {module_name}\n"
                        import_section += process_imports(p, depth + 1)
                        file_imports.append(import_section)
                        found = True
                        break
                
                if not found and item_name:
                    # Try to find specific item being imported
                    for root, dirs, files in os.walk(repo_dir):
                        for file in files:
                            if file == f"{item_name}.py":
                                p = os.path.join(root, file)
                                import_section = f"# Inlined import: {module_name}.{item_name}\n"
                                import_section += process_imports(p, depth + 1)
                                file_imports.append(import_section)
                                processed_modules.add(module_name)
                                found = True
                                break
                        if found:
                            break
            
            # Add filtered code (excluding imports we've processed)
            filtered_code = ""
            lines = code.split('\n')
            for line in lines:
                if line.strip().startswith(('import ', 'from ')):
                    # Skip imports for modules we've inlined
                    if any(module in line for module in processed_modules):
                        filtered_code += f"# {line}  # Import inlined\n"
                        continue
                
                filtered_code += f"{line}\n"
            
            # Combine imports with code
            section = ""
            for imp in file_imports:
                section += imp + "\n"
            section += filtered_code
            
            return section
                
        except SyntaxError:
            return f"# Failed to parse {file_path}\n{code}\n"
    
    # Process the main file
    consolidated_code += process_imports(main_file_path)
    
    # Write the consolidated code
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(consolidated_code)
    
    return True

def build_dataset(videos_file, transcript_dir, repo_dir, output_dir='generate_dataset/3b1b_dataset'):
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
                    
                        # Try to create consolidated file
                        main_files = []
                        
                        # Look for main.py or scene.py or similar key files
                        for file_path in best_match.get('files', []):
                            base_name = os.path.basename(file_path)
                            if base_name in ['main.py', 'scene.py'] or 'scene' in base_name.lower():
                                main_files.append(file_path)
                        
                        # If no main files found, try filename matching the directory
                        if not main_files:
                            dir_name = os.path.basename(best_match['path'])
                            for file_path in best_match.get('files', []):
                                if os.path.basename(file_path) == f"{dir_name}.py":
                                    main_files.append(file_path)
                        
                        # If still no main files, just use the first Python file
                        if not main_files and best_match.get('files'):
                            for file_path in best_match.get('files', []):
                                if file_path.endswith('.py'):
                                    main_files.append(file_path)
                                    break
                        
                        # Create consolidated file(s)
                        if main_files:
                            print(f"  Found {len(main_files)} potential main files for consolidation")
                            for i, main_file in enumerate(main_files[:1]):  # Just use the first main file
                                main_file_path = os.path.join(repo_dir, main_file)
                                consolidated_path = os.path.join(code_dir, f"consolidated_code.py")
                                
                                if os.path.exists(main_file_path):
                                    print(f"  Creating consolidated file from {main_file}")
                                    analyze_imports_and_consolidate(main_file_path, repo_dir, consolidated_path)
                                else:
                                    print(f"  Main file not found: {main_file_path}")
                        else:
                            print(f"  No main files identified for {video['title']}")
                    
                    elif match_type == 'file':
                        # Copy single file
                        print(f"  Copying file: {src_path}")
                        dst_file = os.path.join(code_dir, os.path.basename(src_path))
                        shutil.copy2(src_path, dst_file)
                        
                        # Create consolidated version
                        consolidated_path = os.path.join(code_dir, "consolidated_code.py")
                        print(f"  Creating consolidated file from {src_path}")
                        analyze_imports_and_consolidate(src_path, repo_dir, consolidated_path)
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