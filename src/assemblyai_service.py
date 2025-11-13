"""
AssemblyAI Service
Premium transcription with chapters and speaker detection.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional
import assemblyai as aai

logger = logging.getLogger(__name__)


class AssemblyAIService:
    """Handles transcription using AssemblyAI for long-form content."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AssemblyAI service.
        
        Args:
            api_key: AssemblyAI API key (or from environment)
        """
        self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY')
        
        if self.api_key:
            aai.settings.api_key = self.api_key
            self.enabled = True
            logger.info("AssemblyAI service initialized")
        else:
            self.enabled = False
            logger.warning("AssemblyAI API key not found - service disabled")
    
    def transcribe(self, audio_path: Path, detect_chapters: bool = True, 
                   detect_speakers: bool = False) -> Dict[str, any]:
        """
        Transcribe audio file using AssemblyAI.
        
        Args:
            audio_path: Path to audio file
            detect_chapters: Enable auto-chapter detection
            detect_speakers: Enable speaker diarization
            
        Returns:
            Dict with transcription, chapters, speakers, etc.
        """
        if not self.enabled:
            raise ValueError("AssemblyAI service not enabled - missing API key")
        
        try:
            logger.info(f"Transcribing with AssemblyAI: {audio_path.name}")
            
            # Configure transcription
            config = aai.TranscriptionConfig(
                auto_chapters=detect_chapters,
                speaker_labels=detect_speakers
            )
            
            # Create transcriber
            transcriber = aai.Transcriber()
            
            # Transcribe
            transcript = transcriber.transcribe(str(audio_path), config=config)
            
            # Check for errors
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
            
            # Build result
            result = {
                'text': transcript.text,
                'duration': transcript.audio_duration,
                'word_count': len(transcript.text.split()),
                'chapters': [],
                'speakers': []
            }
            
            # Add chapters if available
            if detect_chapters and transcript.chapters:
                result['chapters'] = [
                    {
                        'start': ch.start / 1000,  # Convert ms to seconds
                        'end': ch.end / 1000,
                        'headline': ch.headline,
                        'summary': ch.summary,
                        'gist': ch.gist
                    }
                    for ch in transcript.chapters
                ]
                logger.info(f"Detected {len(result['chapters'])} chapters")
            
            # Add speaker info if available
            if detect_speakers and transcript.utterances:
                result['speakers'] = [
                    {
                        'speaker': utt.speaker,
                        'start': utt.start / 1000,
                        'end': utt.end / 1000,
                        'text': utt.text
                    }
                    for utt in transcript.utterances
                ]
                logger.info(f"Detected {len(set(s['speaker'] for s in result['speakers']))} speakers")
            
            logger.info(f"✅ AssemblyAI transcription complete: {len(result['text'])} characters")
            return result
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription error: {e}")
            raise
    
    def format_chapters_for_airtable(self, chapters: list) -> str:
        """Format chapters as readable text for Airtable."""
        if not chapters:
            return ""
        
        formatted = []
        for i, ch in enumerate(chapters, 1):
            time_str = f"{int(ch['start']//60):02d}:{int(ch['start']%60):02d}"
            formatted.append(f"{i}. [{time_str}] {ch['headline']}")
            if ch.get('gist'):
                formatted.append(f"   {ch['gist']}")
        
        return '\n\n'.join(formatted)
