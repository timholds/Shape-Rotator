import os
import json
import argparse
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Load environment variables from .env.development file
load_dotenv(dotenv_path='.env.development')

def get_playlist_videos(api_key, playlist_id, verbose=True):
    """
    Retrieves all videos from a YouTube playlist using the YouTube Data API.
    
    Args:
        api_key: Your YouTube Data API key
        playlist_id: The ID of the YouTube playlist
        verbose: Whether to print progress updates
        
    Returns:
        A list of dictionaries containing video metadata in the required format
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    videos = []
    next_page_token = None
    total_processed = 0
    
    try:
        # Paginate through all results
        while True:
            # Get playlist items
            if verbose:
                print(f"Fetching playlist items (page token: {next_page_token or 'None'})")
            
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,  # Maximum allowed per request
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            # Process each video
            if verbose:
                print(f"Processing {len(response['items'])} videos...")
            
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                
                if verbose:
                    total_processed += 1
                    print(f"Processing video {total_processed}: {video_id}")
                
                # Get more detailed video information
                try:
                    video_response = youtube.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=video_id
                    ).execute()
                    
                    if video_response['items']:
                        video_details = video_response['items'][0]
                        snippet = video_details['snippet']
                        published_at = snippet['publishedAt']
                        title = snippet['title']
                        description = snippet['description']
                        duration = video_details['contentDetails']['duration']
                        
                        # Extract year from published date
                        year = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').year
                        
                        # Check if video has transcript
                        has_transcript = check_transcript(video_id)
                        
                        videos.append({
                            'video_id': video_id,
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'title': title,
                            'published_at': published_at,
                            'year': year,
                            'description': description,
                            'duration': duration,
                            'has_transcript': has_transcript
                        })
                    
                except HttpError as e:
                    print(f"Error fetching details for video {video_id}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing video {video_id}: {e}")
            
            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    
    except HttpError as e:
        print(f"HTTP error when accessing YouTube API: {e}")
        if e.resp.status == 404:
            print("Playlist not found. Please check the playlist ID.")
        elif e.resp.status == 403:
            print("Access forbidden. Please check your API key.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return videos

def check_transcript(video_id):
    """
    Checks if a YouTube video has a transcript available.
    
    Args:
        video_id: The YouTube video ID
        
    Returns:
        Boolean indicating if transcript is available
    """
    try:
        YouTubeTranscriptApi.get_transcript(video_id)
        return True
    except (TranscriptsDisabled, NoTranscriptFound):
        return False
    except Exception as e:
        print(f"Error checking transcript for video {video_id}: {e}")
        return False

def save_playlist_data(videos, output_file='playlist_videos.json'):
    """Save the video metadata to a JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"Saved metadata for {len(videos)} videos to {output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract data from a YouTube playlist')
    parser.add_argument('--playlist-id', required=True, help='ID of the YouTube playlist')
    parser.add_argument('--output', default='generate_dataset/playlist_videos.json', help='Output JSON file path')
    parser.add_argument('--api-key', help='YouTube Data API key (overrides environment variable)')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress updates')
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: No YouTube API key found. Please set the YOUTUBE_API_KEY environment variable or use --api-key.")
        return
    
    print(f"Retrieving videos from playlist: {args.playlist_id}")
    videos = get_playlist_videos(api_key, args.playlist_id, verbose=not args.quiet)
    save_playlist_data(videos, args.output)
    
    print("\nNOTE: This script automatically uses your YOUTUBE_API_KEY from the .env file")
    print("Playlist ID can be found in the URL: https://www.youtube.com/playlist?list=PLAYLIST_ID")

if __name__ == '__main__':
    main()