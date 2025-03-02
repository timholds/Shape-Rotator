import os
from googleapiclient.discovery import build
import json
from datetime import datetime

def get_all_3b1b_videos(api_key):
    """
    Retrieves all videos from the 3Blue1Brown YouTube channel using the YouTube Data API.
    
    Args:
        api_key: Your YouTube Data API key
        
    Returns:
        A list of dictionaries containing video metadata
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 3Blue1Brown channel ID
    channel_id = 'UCYO_jab_esuFRV4b17AJtAw'
    
    videos = []
    next_page_token = None
    
    # Paginate through all results
    while True:
        # Get videos from channel, sorted by date
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=50,  # Maximum allowed per request
            order='date',
            type='video',
            pageToken=next_page_token
        )
        
        response = request.execute()
        
        # Process each video
        for item in response['items']:
            video_id = item['id']['videoId']
            
            # Get more detailed video information
            video_response = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if video_response['items']:
                video_details = video_response['items'][0]
                published_at = video_details['snippet']['publishedAt']
                title = video_details['snippet']['title']
                description = video_details['snippet']['description']
                
                # Extract year for GitHub repo matching
                year = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').year
                
                videos.append({
                    'video_id': video_id,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'title': title,
                    'published_at': published_at,
                    'year': year,
                    'description': description
                })
        
        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return videos

def save_video_metadata(videos, output_file='3b1b_videos.json'):
    """Save the video metadata to a JSON file"""
    with open(output_file, 'w') as f:
        json.dump(videos, f, indent=2)
    print(f"Saved metadata for {len(videos)} videos to {output_file}")

if __name__ == '__main__':
    # You'll need to set your API key
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        api_key = input("Enter your YouTube API key: ")
    
    videos = get_all_3b1b_videos(api_key)
    save_video_metadata(videos)