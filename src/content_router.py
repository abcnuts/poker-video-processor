"""
Content Router
Detects content type and routes to appropriate processor.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple
import subprocess
import requests

logger = logging.getLogger(__name__)


class ContentRouter:
    """Routes content to appropriate processor based on type and size."""
    
    # File size thresholds (in bytes)
    SMALL_FILE_LIMIT = 25 * 1024 * 1024  # 25MB
    MEDIUM_FILE_LIMIT = 100 * 1024 * 1024  # 100MB
    
    # Document extensions
    DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.md', '.markdown', '.txt'}
    
    # Audio/Video extensions
    MEDIA_EXTENSIONS = {'.mp3', '.mp4', '.wav', '.m4a', '.mov', '.avi', '.mkv', '.webm'}
    
    def __init__(self):
        pass
    
    def detect_content_type(self, url: str) -> Tuple[str, Dict]:
        """
        Detect content type and return processing strategy.
        
        Args:
            url: URL or file path
            
        Returns:
            Tuple of (content_type, metadata)
            content_type: 'document', 'audio', 'video', 'url'
            metadata: Dict with size, format, processing_method, etc.
        """
        try:
            # Check if it's a web URL
            if url.startswith('http://') or url.startswith('https://'):
                return self._detect_url_type(url)
            
            # Check if it's a local file
            path = Path(url)
            if path.exists():
                return self._detect_file_type(path)
            
            # Assume it's a URL that needs downloading
            return 'video', {'processing_method': 'download_first', 'url': url}
            
        except Exception as e:
            logger.error(f"Error detecting content type: {e}")
            return 'unknown', {'error': str(e)}
    
    def _detect_url_type(self, url: str) -> Tuple[str, Dict]:
        """Detect type of content from URL."""
        # Check for common video platforms
        video_platforms = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com']
        if any(platform in url.lower() for platform in video_platforms):
            return 'video', {'processing_method': 'yt-dlp', 'url': url}
        
        # Check for direct file links
        ext = Path(url).suffix.lower()
        if ext in self.DOCUMENT_EXTENSIONS:
            return 'document', {'processing_method': 'download_and_extract', 'url': url, 'extension': ext}
        elif ext in self.MEDIA_EXTENSIONS:
            return 'video', {'processing_method': 'download_first', 'url': url, 'extension': ext}
        
        # Assume it's a web article
        return 'url', {'processing_method': 'web_scrape', 'url': url}
    
    def _detect_file_type(self, path: Path) -> Tuple[str, Dict]:
        """Detect type of local file."""
        ext = path.suffix.lower()
        file_size = path.stat().st_size
        
        # Document files
        if ext in self.DOCUMENT_EXTENSIONS:
            return 'document', {
                'processing_method': 'extract_text',
                'path': str(path),
                'extension': ext,
                'size': file_size
            }
        
        # Media files
        if ext in self.MEDIA_EXTENSIONS:
            # Determine processing method based on size
            if file_size < self.SMALL_FILE_LIMIT:
                method = 'openai_whisper'
            elif file_size < self.MEDIUM_FILE_LIMIT:
                method = 'chunk_and_stitch'
            else:
                method = 'assemblyai'
            
            return 'video', {
                'processing_method': method,
                'path': str(path),
                'extension': ext,
                'size': file_size,
                'size_mb': file_size / (1024 * 1024)
            }
        
        return 'unknown', {'path': str(path), 'extension': ext}
    
    def get_file_duration(self, path: Path) -> float:
        """Get duration of audio/video file in seconds."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
            return 0.0
    
    def should_use_assemblyai(self, file_size: int, duration: float = 0) -> bool:
        """
        Determine if AssemblyAI should be used based on file characteristics.
        
        Args:
            file_size: File size in bytes
            duration: Duration in seconds (optional)
            
        Returns:
            True if AssemblyAI should be used
        """
        # Use AssemblyAI for files over 100MB
        if file_size > self.MEDIUM_FILE_LIMIT:
            return True
        
        # Use AssemblyAI for content over 1 hour
        if duration > 3600:
            return True
        
        return False
