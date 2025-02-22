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
            region_name="sfo3",  # Replace with your region
            endpoint_url="https://sfo3.digitaloceanspaces.com",  # Replace with your endpoint
            aws_access_key_id=os.getenv("SPACES_KEY"),
            aws_secret_access_key=os.getenv("SPACES_SECRET")
        )
        self.bucket = os.getenv("SPACES_BUCKET")
        self.cdn_domain = os.getenv("SPACES_CDN_DOMAIN")  # e.g., "cdn.yourdomain.com"

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
            # Create a videos/ prefix to organize files
            key = f"videos/{task_id}/animation.mp4"
            
            # Upload the file
            self.client.upload_file(
                str(video_path),
                self.bucket,
                key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'video/mp4'
                }
            )
            
            # Return CDN URL if configured, otherwise direct Spaces URL
            if self.cdn_domain:
                return f"https://{self.cdn_domain}/{key}"
            return f"https://{self.bucket}.nyc3.digitaloceanspaces.com/{key}"
            
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
            
            # Return CDN URL if configured, otherwise direct Spaces URL
            if self.cdn_domain:
                return f"https://{self.cdn_domain}/{key}"
            return f"https://{self.bucket}.nyc3.digitaloceanspaces.com/{key}"
            
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