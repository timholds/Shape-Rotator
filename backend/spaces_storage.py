from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional
import logging
import asyncio
from datetime import datetime, timedelta
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class SpacesStorage:
    def __init__(self):
        self.session = boto3.session.Session()
        
        # Validate environment variables
        required_vars = ["SPACES_KEY", "SPACES_SECRET", "SPACES_BUCKET"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        self.client = self.session.client('s3',
            region_name="sfo3",
            endpoint_url="https://sfo3.digitaloceanspaces.com",
            aws_access_key_id=os.getenv("SPACES_KEY"),
            aws_secret_access_key=os.getenv("SPACES_SECRET")
        )
        self.bucket = os.getenv("SPACES_BUCKET")
        
        # Validate bucket access on startup
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"Successfully connected to Spaces bucket: {self.bucket}")
        except ClientError as e:
            raise ValueError(f"Failed to access Spaces bucket {self.bucket}: {str(e)}")

    async def compress_video(self, input_path: Path) -> Optional[Path]:
        """Compress video using ffmpeg before upload."""
        try:
            output_path = input_path.with_suffix('.compressed.mp4')
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libx264', '-crf', '23',
                '-preset', 'medium',
                '-y',  # Overwrite output file if it exists
                str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Video compression failed: {stderr.decode()}")
                return None
                
            if output_path.exists() and output_path.stat().st_size < input_path.stat().st_size:
                return output_path
            return None
            
        except Exception as e:
            logger.warning(f"Error during video compression: {str(e)}")
            return None

    async def upload_video(self, video_path: Path, task_id: str) -> Optional[str]:
        """Upload a video file to DigitalOcean Spaces with compression."""
        try:
            # Try to compress the video first
            compressed_path = await self.compress_video(video_path)
            upload_path = compressed_path if compressed_path else video_path
            
            key = f"videos/{task_id}/animation.mp4"
            
            # Upload with progress logging
            file_size = upload_path.stat().st_size
            logger.info(f"Starting upload of {file_size} bytes for task {task_id}")
            
            self.client.upload_file(
                str(upload_path),
                self.bucket,
                key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'video/mp4',
                    'CacheControl': 'max-age=31536000'  # Cache for 1 year
                }
            )
            
            logger.info(f"Successfully uploaded video for task {task_id}")
            
            # Clean up compressed file if it exists
            if compressed_path and compressed_path.exists():
                compressed_path.unlink()
            
            return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
            
        except ClientError as e:
            logger.error(f"Failed to upload video for task {task_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during upload for task {task_id}: {str(e)}")
            return None

    async def cleanup_old_videos(self, max_age_hours: int = 24):
        """Remove videos older than specified hours."""
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            
            # Get timestamp for comparison
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            count = 0
            total_size = 0
            
            for page in paginator.paginate(Bucket=self.bucket, Prefix='videos/'):
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_time:
                        self.client.delete_object(
                            Bucket=self.bucket,
                            Key=obj['Key']
                        )
                        count += 1
                        total_size += obj['Size']
            
            if count > 0:
                logger.info(f"Cleaned up {count} videos ({total_size/1024/1024:.2f} MB)")
                
        except Exception as e:
            logger.error(f"Error during video cleanup: {str(e)}")

    async def get_video_url(self, task_id: str) -> Optional[str]:
        """Get the URL for a video stored in Spaces."""
        try:
            key = f"videos/{task_id}/animation.mp4"
            self.client.head_object(Bucket=self.bucket, Key=key)
            return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
        except ClientError:
            return None
        
    async def upload_code(self, code: str, task_id: str) -> Optional[str]:
        """Upload a code string to DigitalOcean Spaces."""
        try:
            key = f"videos/{task_id}/code.py"
            
            # Create a temporary file to upload
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name
            logger.info(f"Created temporary file at {temp_path}")
                        
            # Log the upload
            logger.info(f"Uploading code for task {task_id}")
            
            try:
                self.client.upload_file(
                    temp_path,
                    self.bucket,
                    key,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': 'text/plain',
                        'CacheControl': 'max-age=31536000'  # Cache for 1 year
                    }
                )
                
                # Clean up temp file
                os.unlink(temp_path)
                
                logger.info(f"Successfully uploaded code for task {task_id}")
                return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
                
            except Exception as e:
                logger.error(f"Error in upload operation for task {task_id}: {str(e)}", exc_info=True)
                return None
            finally:
                # Ensure temp file is removed
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info(f"Cleaned up temp file for task {task_id}")
                
        except Exception as e:
            logger.error(f"Unexpected error during code upload for task {task_id}: {str(e)}")
            return None
    
    async def get_code_url(self, task_id: str) -> Optional[str]:
        """Get the URL for code stored in Spaces."""
        try:
            key = f"videos/{task_id}/code.py"
            self.client.head_object(Bucket=self.bucket, Key=key)
            return f"https://{self.bucket}.sfo3.digitaloceanspaces.com/{key}"
        except ClientError:
            return None