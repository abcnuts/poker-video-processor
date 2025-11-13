"""
Poker Video Processor
Downloads videos, extracts audio, transcribes, and extracts poker insights.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional
import yt_dlp
from openai import OpenAI

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video download, transcription, and insight extraction."""
    
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
    def process_video(self, video_url: str, record_id: str) -> Dict[str, str]:
        """
        Process a video from URL to transcription and insights.
        
        Args:
            video_url: URL of the video to process
            record_id: Airtable record ID for logging
            
        Returns:
            Dict with transcription, key_quotes, core_philosophy, and status
        """
        logger.info(f"Processing video {record_id}: {video_url}")
        
        try:
            # Step 1: Download video
            video_path = self._download_video(video_url, record_id)
            logger.info(f"✅ Downloaded: {video_path}")
            
            # Step 2: Extract audio (or use directly if already audio-only)
            if self._is_audio_file(video_path):
                # File is already audio-only, rename to .mp3
                audio_path = video_path.with_suffix('.mp3')
                video_path.rename(audio_path)
                logger.info(f"✅ Audio-only file detected: {audio_path}")
            else:
                # Extract audio from video
                audio_path = self._extract_audio(video_path)
                logger.info(f"✅ Extracted audio: {audio_path}")
            
            # Step 3: Transcribe
            transcription = self._transcribe_audio(audio_path)
            logger.info(f"✅ Transcribed: {len(transcription)} characters")
            
            # Step 4: Extract insights
            insights = self._extract_insights(transcription)
            logger.info(f"✅ Extracted insights")
            
            # Cleanup
            self._cleanup_files(video_path, audio_path)
            
            return {
                "transcription": transcription,
                "key_quotes": insights["key_quotes"],
                "core_philosophy": insights["core_philosophy"],
                "status": "Extracted"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing {record_id}: {str(e)}")
            return {
                "transcription": f"ERROR: {str(e)}",
                "status": "Raw"
            }
    
    def _download_video(self, url: str, record_id: str) -> Path:
        """Download video using yt-dlp."""
        output_path = self.download_dir / f"{record_id}.mp4"
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_path
    
    def _is_audio_file(self, file_path: Path) -> bool:
        """Check if file is audio-only (no video stream)."""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == ''  # No video stream = audio only
    
    def _extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video using ffmpeg."""
        audio_path = video_path.with_suffix('.mp3')
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-q:a', '2',  # High quality
            '-y',  # Overwrite
            str(audio_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path
    
    def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio using OpenAI Whisper."""
        with open(audio_path, 'rb') as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    
    def _extract_insights(self, transcription: str) -> Dict[str, str]:
        """Extract poker insights using AI."""
        
        prompt = f"""Analyze this poker content transcription and extract:

1. KEY QUOTES: 3-5 memorable, tweetable quotes (each under 280 chars)
2. CORE PHILOSOPHY: The main poker philosophy or strategy being taught (2-3 sentences)

Transcription:
{transcription}

Format your response as:

KEY QUOTES:
- [quote 1]
- [quote 2]
- [quote 3]

CORE PHILOSOPHY:
[2-3 sentence summary]
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a poker strategy expert who extracts key insights from poker content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse the response
        parts = content.split("CORE PHILOSOPHY:")
        quotes_section = parts[0].replace("KEY QUOTES:", "").strip()
        philosophy_section = parts[1].strip() if len(parts) > 1 else ""
        
        return {
            "key_quotes": quotes_section,
            "core_philosophy": philosophy_section
        }
    
    def _cleanup_files(self, video_path: Path, audio_path: Path):
        """Remove temporary files."""
        try:
            if video_path.exists():
                video_path.unlink()
            if audio_path.exists():
                audio_path.unlink()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
