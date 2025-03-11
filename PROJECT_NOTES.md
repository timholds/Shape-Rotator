In dataset_builder.py, we need to modify the code handling section to:
- Identify the "main" file for the video
- Scan that file for imports from the repository (not standard libraries)
- Generate a new "complete" file that includes the imported code


3/9/25: Current Repository Exploration Approach:
-Look for directories matching the video's year (and adjacent years)
- Pre-filter candidates based on simplistic rules
- Process each candidate individually with LLM
- Sort the results by confidence

This approach has limitations, namely that it doesn't account for the complex repository structure. By handling each of the candidate in isolation, it also prevents comparison between the different options!

# Current Dataset Structure
output_dir/ (e.g., 'generate_dataset/3b1b_dataset/')
├── index.json          # Summary of the entire dataset
├── [video_id_1]/       # Directory for each video
│   ├── metadata.json   # All video metadata
│   ├── transcript_clean.txt      # Clean transcript without timestamps
│   ├── transcript_timestamped.txt # Transcript with timestamps 
│   └── code/           # Directory for the related code
│       ├── README.md   # Match information (confidence, type, path)
│       ├── [code files from repo]  # Actual Python files
│       └── run_manim.py  # Helper script to run the code (for directory matches)
├── [video_id_2]/

# 3b1b Repository Structure
- Direct 1:1 files: Single Python files corresponding to one video
- 1:1 directories: Directories containing files for a single video
- Series directories: Directories with shared files used by multiple videos (transformers/)
- Mixed directories: Containing both standalone files and subdirectories (2018 with eop/)
- Imported dependencies: Files that are imported across projects
# RL Pipeline: 
GenerationAttempt class, we're capturing:
Basic Metadata:
- timestamp
- model_version ("mistral")
- system_prompt
- user_query

Generation Details:
- generated_code
- execution_outcome:
    - status (completed/failed)
    - error message (if failed)