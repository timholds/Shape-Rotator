# 3Blue1Brown Dataset Collection

This project creates a dataset pairing 3Blue1Brown videos with their corresponding Manim code and transcripts.

## What this collects:

- **Video metadata**: Titles, descriptions, publication dates, etc.
- **Transcripts**: Text captions from the videos
- **Manim code**: The source code used to create the animations

> **Note**: This does NOT download any actual video files - only text and code data.

## Requirements

1. Python 3.7 or higher
2. YouTube Data API key (placed in `.env.development` file)
3. Internet connection

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env.development` file with your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## Running the Collection

```bash
python generate_data/run_dataset_generation.py
```

Or to skip certain steps:

```bash
python generate_data/run_dataset_generation.py --skip-videos --skip-transcripts
```

## Resulting Dataset Structure

The generated dataset will have the following structure:

```
3b1b_dataset/
├── index.json                # Complete metadata index
├── video_id_1/               # Directory for each video
│   ├── metadata.json         # Video metadata
│   ├── transcript_clean.txt  # Plain transcript text
│   ├── transcript_timestamped.txt  # Transcript with timestamps
│   └── code/                 # Source code
│       ├── README.md         # Info about the code match
│       ├── run_manim.py      # Helper script to run the code
│       └── *.py              # Actual Manim source files
├── video_id_2/
└── ...
```

## Dataset Size

The complete dataset should be relatively small (typically less than a few hundred MB) since it only contains text and code, not video files.

## Usage Tips

1. Each video directory contains a `code/README.md` file with information about how the code was matched to the video.
2. For directories that contain Manim code, a `run_manim.py` helper script is provided to assist with running the animations.
3. Match confidence scores range from 0-100+, with higher scores indicating more confident matches.


# Matching videos to code
`python generate_dataset/tools.py manual-match`
`python generate_dataset/tools.py manual-match`
`python generate_dataset/print_missing_videos.py`