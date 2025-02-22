from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from fastapi.responses import RedirectResponse
import os
from typing import Optional

class SpacesStorage:
    def __init__(self):
        self.session = boto3.session.Session()
        self.client = self.session.client('s3',
            region_name="sfo3",  # San Francisco region
            endpoint_url="https://sfo3.digitaloceanspaces.com",  # SFO3 endpoint
            aws_access_key_id=os.getenv("SPACES_KEY"),
            aws_secret_access_key=os.getenv("SPACES_SECRET")
        )
        self.bucket = os.getenv("SPACES_BUCKET")

    async def upload_video(self, video_path: Path, task_id: str) -> Optional[str]:
        """
        Upload a video file to DigitalOcean Spaces.
        
        Args:
            video_path: Path to the local video file
            task_id: Unique identifier for the video
            
        Returns:
            URL of the uploaded video if successful, None otherwise
        """
        try:
            key = f"videos/{task_id}/animation.mp4"
            
            self.client.upload_file(
                str(video_path),
                self.bucket,
                key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'video/mp4'
                }
            )
            
            return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
            
        except ClientError as e:
            print(f"Error uploading to Spaces: {str(e)}")
            return None

    async def get_video_url(self, task_id: str) -> Optional[str]:
        """
        Get the URL for a video stored in Spaces.
        
        Args:
            task_id: Unique identifier for the video
            
        Returns:
            URL of the video if it exists, None otherwise
        """
        try:
            key = f"videos/{task_id}/animation.mp4"
            
            # Check if object exists
            self.client.head_object(Bucket=self.bucket, Key=key)
            
            return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
            
        except ClientError:
            return None

    async def delete_video(self, task_id: str) -> bool:
        """
        Delete a video from Spaces.
        
        Args:
            task_id: Unique identifier for the video
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            key = f"videos/{task_id}/animation.mp4"
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False