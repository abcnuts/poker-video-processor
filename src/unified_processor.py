"""
Unified Content Processor
Routes content to appropriate processor based on type and size.
"""

import os
import logging
from pathlib import Path
from typing import Dict
from openai import OpenAI

from content_router import ContentRouter
from document_processor import DocumentProcessor
from video_processor import VideoProcessor
from audio_chunker import AudioChunker
from assemblyai_service import AssemblyAIService

logger = logging.getLogger(__name__)


class UnifiedProcessor:
    """Unified processor that handles all content types."""
    
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all processors
        self.router = ContentRouter()
        self.doc_processor = DocumentProcessor()
        self.video_processor = VideoProcessor(download_dir=str(self.download_dir))
        self.audio_chunker = AudioChunker(chunk_duration=1200)  # 20 min chunks
        self.assemblyai = AssemblyAIService()
        self.openai_client = OpenAI()
    
    def process_content(self, url: str, record_id: str) -> Dict[str, str]:
        """
        Process any type of content and extract insights.
        
        Args:
            url: URL or file path to content
            record_id: Airtable record ID
            
        Returns:
            Dict with transcription/text, quotes, philosophy, status
        """
        try:
            # Detect content type
            content_type, metadata = self.router.detect_content_type(url)
            logger.info(f"Content type: {content_type}, Method: {metadata.get('processing_method')}")
            
            # Route to appropriate processor
            if content_type == 'document':
                return self._process_document(url, metadata)
            elif content_type == 'url':
                return self._process_url(url, metadata)
            elif content_type == 'video':
                return self._process_media(url, record_id, metadata)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            return {
                "transcription": f"ERROR: {str(e)}",
                "status": "Raw"
            }
    
    def _process_document(self, url: str, metadata: Dict) -> Dict[str, str]:
        """Process document (PDF, Word, Markdown, etc.)."""
        logger.info(f"Processing document: {url}")
        
        # Extract text
        text = self.doc_processor.extract_text(url)
        
        if not text:
            raise ValueError("Could not extract text from document")
        
        logger.info(f"✅ Extracted text: {len(text)} characters")
        
        # Extract insights
        insights = self._extract_insights(text)
        
        return {
            "transcription": text[:10000],  # Limit to first 10k chars for Airtable
            "key_quotes": insights["key_quotes"],
            "core_philosophy": insights["core_philosophy"],
            "status": "Extracted"
        }
    
    def _process_url(self, url: str, metadata: Dict) -> Dict[str, str]:
        """Process web article."""
        logger.info(f"Processing web article: {url}")
        
        # Extract text from URL
        text = self.doc_processor.extract_text(url)
        
        if not text:
            raise ValueError("Could not extract text from URL")
        
        logger.info(f"✅ Extracted text: {len(text)} characters")
        
        # Extract insights
        insights = self._extract_insights(text)
        
        return {
            "transcription": text[:10000],
            "key_quotes": insights["key_quotes"],
            "core_philosophy": insights["core_philosophy"],
            "status": "Extracted"
        }
    
    def _process_media(self, url: str, record_id: str, metadata: Dict) -> Dict[str, str]:
        """Process audio/video content."""
        method = metadata.get('processing_method')
        
        # Download video first if needed
        if method in ['yt-dlp', 'download_first']:
            logger.info(f"Downloading media: {url}")
            video_path = self.video_processor._download_video(url, record_id)
            
            # Check if it's audio-only
            if self.video_processor._is_audio_file(video_path):
                audio_path = video_path.with_suffix('.mp3')
                video_path.rename(audio_path)
            else:
                audio_path = self.video_processor._extract_audio(video_path)
                video_path.unlink()  # Delete video after extracting audio
            
            logger.info(f"✅ Audio ready: {audio_path}")
        else:
            audio_path = Path(metadata['path'])
        
        # Determine transcription method based on file size
        file_size = audio_path.stat().st_size
        duration = self.router.get_file_duration(audio_path)
        
        logger.info(f"File size: {file_size/(1024*1024):.1f}MB, Duration: {duration/60:.1f}min")
        
        # Choose transcription method
        if self.assemblyai.enabled and self.router.should_use_assemblyai(file_size, duration):
            transcription = self._transcribe_with_assemblyai(audio_path, duration)
        elif file_size > self.router.SMALL_FILE_LIMIT:
            transcription = self._transcribe_with_chunking(audio_path)
        else:
            transcription = self.video_processor._transcribe_audio(audio_path)
        
        logger.info(f"✅ Transcribed: {len(transcription)} characters")
        
        # Extract insights
        insights = self._extract_insights(transcription)
        
        # Cleanup
        if audio_path.exists():
            audio_path.unlink()
        
        return {
            "transcription": transcription[:10000],
            "key_quotes": insights["key_quotes"],
            "core_philosophy": insights["core_philosophy"],
            "status": "Extracted"
        }
    
    def _transcribe_with_assemblyai(self, audio_path: Path, duration: float) -> str:
        """Transcribe using AssemblyAI (premium, with chapters)."""
        logger.info(f"Using AssemblyAI for {duration/60:.1f} minute audio")
        
        # Enable chapters for content over 10 minutes
        detect_chapters = duration > 600
        
        result = self.assemblyai.transcribe(audio_path, detect_chapters=detect_chapters)
        
        # If chapters detected, include them in transcription
        if result.get('chapters'):
            chapters_text = self.assemblyai.format_chapters_for_airtable(result['chapters'])
            return f"{result['text']}\n\n--- CHAPTERS ---\n{chapters_text}"
        
        return result['text']
    
    def _transcribe_with_chunking(self, audio_path: Path) -> str:
        """Transcribe large file by chunking."""
        logger.info("Using chunk & stitch method")
        
        # Create chunks directory
        chunks_dir = audio_path.parent / f"{audio_path.stem}_chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        try:
            # Split audio
            chunks = self.audio_chunker.split_audio(audio_path, chunks_dir)
            
            # Transcribe each chunk
            transcriptions = []
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"Transcribing chunk {i}/{len(chunks)}")
                text = self.video_processor._transcribe_audio(chunk)
                transcriptions.append(text)
            
            # Stitch together
            full_transcription = self.audio_chunker.stitch_transcriptions(transcriptions)
            
            return full_transcription
            
        finally:
            # Cleanup chunks
            self.audio_chunker.cleanup_chunks(chunks)
            if chunks_dir.exists():
                chunks_dir.rmdir()
    
    def _extract_insights(self, text: str) -> Dict[str, str]:
        """Extract insights using AI (same as video_processor)."""
        prompt = f"""Analyze this poker content and extract:

1. KEY QUOTES: 5-7 memorable, tweetable quotes (each under 280 chars)
2. CORE PHILOSOPHY: The main poker philosophy or strategy being taught (3-4 sentences)

Content:
{text[:15000]}  

Format your response as:

KEY QUOTES:
- [quote 1]
- [quote 2]
etc.

CORE PHILOSOPHY:
[3-4 sentence summary]
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a poker strategy expert who extracts key insights from poker content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        # Parse response
        parts = content.split("CORE PHILOSOPHY:")
        quotes_section = parts[0].replace("KEY QUOTES:", "").strip()
        philosophy_section = parts[1].strip() if len(parts) > 1 else ""
        
        return {
            "key_quotes": quotes_section,
            "core_philosophy": philosophy_section
        }
