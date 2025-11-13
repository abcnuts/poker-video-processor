"""
Audio Chunker
Splits large audio files into manageable chunks for transcription.
"""

import logging
import subprocess
from pathlib import Path
from typing import List
import math

logger = logging.getLogger(__name__)


class AudioChunker:
    """Handles splitting and stitching of large audio files."""
    
    def __init__(self, chunk_duration: int = 1200):
        """
        Initialize chunker.
        
        Args:
            chunk_duration: Duration of each chunk in seconds (default 20 minutes)
        """
        self.chunk_duration = chunk_duration
    
    def get_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds."""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    
    def split_audio(self, audio_path: Path, output_dir: Path) -> List[Path]:
        """
        Split audio file into chunks.
        
        Args:
            audio_path: Path to audio file
            output_dir: Directory to save chunks
            
        Returns:
            List of chunk file paths
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get total duration
            duration = self.get_duration(audio_path)
            num_chunks = math.ceil(duration / self.chunk_duration)
            
            logger.info(f"Splitting {audio_path.name} into {num_chunks} chunks ({duration:.1f}s total)")
            
            chunks = []
            
            for i in range(num_chunks):
                start_time = i * self.chunk_duration
                chunk_path = output_dir / f"{audio_path.stem}_chunk_{i:03d}.mp3"
                
                cmd = [
                    'ffmpeg',
                    '-i', str(audio_path),
                    '-ss', str(start_time),
                    '-t', str(self.chunk_duration),
                    '-acodec', 'libmp3lame',
                    '-q:a', '2',
                    '-y',
                    str(chunk_path)
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                chunks.append(chunk_path)
                logger.info(f"Created chunk {i+1}/{num_chunks}: {chunk_path.name}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            raise
    
    def stitch_transcriptions(self, transcriptions: List[str]) -> str:
        """
        Combine multiple transcriptions into one.
        
        Args:
            transcriptions: List of transcription texts
            
        Returns:
            Combined transcription
        """
        # Join with double newline for readability
        return '\n\n'.join(transcriptions)
    
    def cleanup_chunks(self, chunks: List[Path]):
        """Delete chunk files after processing."""
        for chunk in chunks:
            try:
                if chunk.exists():
                    chunk.unlink()
            except Exception as e:
                logger.warning(f"Could not delete chunk {chunk}: {e}")
