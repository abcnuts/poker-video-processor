"""
Document Processor
Extracts text from PDFs, Word docs, Markdown, and web articles.
"""

import logging
from pathlib import Path
from typing import Optional
import requests
from PyPDF2 import PdfReader
from docx import Document
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles text extraction from various document formats."""
    
    def __init__(self):
        pass
    
    def extract_text(self, source: str) -> Optional[str]:
        """
        Extract text from a document source.
        
        Args:
            source: File path or URL
            
        Returns:
            Extracted text or None if failed
        """
        try:
            # Check if it's a URL
            if source.startswith('http://') or source.startswith('https://'):
                return self._extract_from_url(source)
            
            # Check if it's a file path
            path = Path(source)
            if not path.exists():
                logger.error(f"File not found: {source}")
                return None
            
            # Route to appropriate extractor based on extension
            ext = path.suffix.lower()
            
            if ext == '.pdf':
                return self._extract_from_pdf(path)
            elif ext in ['.docx', '.doc']:
                return self._extract_from_docx(path)
            elif ext in ['.md', '.markdown']:
                return self._extract_from_markdown(path)
            elif ext == '.txt':
                return self._extract_from_txt(path)
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None
    
    def _extract_from_pdf(self, path: Path) -> str:
        """Extract text from PDF."""
        reader = PdfReader(path)
        text = []
        
        for page in reader.pages:
            text.append(page.extract_text())
        
        return '\n\n'.join(text)
    
    def _extract_from_docx(self, path: Path) -> str:
        """Extract text from Word document."""
        doc = Document(path)
        text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return '\n\n'.join(text)
    
    def _extract_from_markdown(self, path: Path) -> str:
        """Extract text from Markdown file."""
        with open(path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Convert markdown to HTML then extract text
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        
        return soup.get_text()
    
    def _extract_from_txt(self, path: Path) -> str:
        """Extract text from plain text file."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_from_url(self, url: str) -> str:
        """Extract text from web article."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get text from article or main content
        article = soup.find('article') or soup.find('main') or soup.find('body')
        
        if article:
            # Get text from paragraphs
            paragraphs = article.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            return text
        
        return soup.get_text()
