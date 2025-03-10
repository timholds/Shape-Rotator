import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def download_transcripts(videos_file, output_dir='transcripts'):
    """
    Downloads transcripts for all videos in the provided JSON file.
    
    Args:
        videos_file: Path to the JSON file containing video metadata
        output_dir: Directory to save transcripts to
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load video metadata
    with open(videos_file, 'r') as f:
        videos = json.load(f)
    
    success_count = 0
    fail_count = 0
    
    # Download transcript for each video
    for i, video in enumerate(videos):
        video_id = video['video_id']
        title = video['title']
        
        print(f"Processing {i+1}/{len(videos)}: {title}")
        
        try:
            # Get the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Convert to plain text with timestamps
            transcript_text = ""
            for entry in transcript:
                start_time = entry['start']
                # Format time as HH:MM:SS
                hours, remainder = divmod(start_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                
                transcript_text += f"[{time_str}] {entry['text']}\n"
            
            # Also create a clean version without timestamps
            clean_text = " ".join([entry['text'] for entry in transcript])
            
            # Save both versions
            with open(f"{output_dir}/{video_id}_timestamped.txt", "w", encoding="utf-8") as f:
                f.write(transcript_text)
            
            with open(f"{output_dir}/{video_id}_clean.txt", "w", encoding="utf-8") as f:
                f.write(clean_text)
            
            # Update video metadata with transcript status
            video['has_transcript'] = True
            success_count += 1
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"  Error: No transcript available - {str(e)}")
            video['has_transcript'] = False
            fail_count += 1
        except Exception as e:
            print(f"  Error: {str(e)}")
            video['has_transcript'] = False
            fail_count += 1
    
    # Save updated metadata
    with open(videos_file, 'w') as f:
        json.dump(videos, f, indent=2)
    
    print(f"Transcript download complete. Success: {success_count}, Failed: {fail_count}")

if __name__ == '__main__':
    download_transcripts('generate_dataset/3b1b_videos.json')