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


There is just one dataaset file that corresponds to each video, but there may also be other helper files we can identify from the imports. 

The transcript should help with matches. 

# TODO Dataset Generation
- [ ] chunking up the code and transcripts
[ ] reward function
[ ] potentiaupdating old code to be new code
[ ] make it so we can run the code from any one dataset dir and regenerate the (chunk of the) 3b1b video
[ ] data augmentations for the summary (length, different ways to describe, level of technicality)
[ ] does the timed info in the transcripts provide a useful signal? perhaps we force one model to generate a transcript and get the other model to try and follow it
[ ] give an agent access to a code interpreter and have it try to run 
    - [ ] use crew ai to try and give some roles 

make this a visual reasoning project, try to force the model to do certain types of thinking like considering how hard a chunk would be to implement

coding tags to try to make the model use 
<code> <math>  

<understand_gestalt>
<related_ideas> <prerequisites>
<illutrative_example> <find_illustrative_values>
<generate_video_transcript>
<execute_code>
<layout> <visual>
<self_check> <self_debug> <modernize_manim>


# (Attempt 1) File Structure
```
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