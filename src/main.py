"""
Poker Video Processor Service
Main orchestrator that polls Airtable and processes videos.
"""

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

from unified_processor import UnifiedProcessor
from airtable_client import AirtableClient

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "processor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PokerVideoService:
    """Main service that orchestrates video processing."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.airtable = AirtableClient(
            api_key=os.getenv("AIRTABLE_API_KEY"),
            base_id=os.getenv("AIRTABLE_BASE_ID"),
            table_id=os.getenv("AIRTABLE_TABLE_ID")
        )
        
        download_dir = Path(__file__).parent.parent / "downloads"
        self.processor = UnifiedProcessor(download_dir=str(download_dir))
        
        self.poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))  # 5 minutes default
        
    def process_pending_videos(self):
        """Process all pending videos in Airtable."""
        logger.info("🔍 Checking for pending videos...")
        
        pending = self.airtable.get_pending_videos()
        
        if not pending:
            logger.info("No pending videos found")
            return
        
        logger.info(f"📹 Found {len(pending)} videos to process")
        
        for record in pending:
            record_id = record['id']
            video_url = record['fields'].get('Source File/Link')
            title = record['fields'].get('Content Title', 'Untitled')
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {title}")
            logger.info(f"Record ID: {record_id}")
            logger.info(f"URL: {video_url}")
            logger.info(f"{'='*60}\n")
            
            # Mark as processing to avoid duplicates
            self.airtable.mark_as_processing(record_id)
            
            try:
                # Process the content (video, audio, or document)
                results = self.processor.process_content(video_url, record_id)
                
                # Update Airtable with results
                success = self.airtable.update_record(record_id, results)
                
                if success:
                    logger.info(f"✅ Successfully processed: {title}\n")
                else:
                    logger.error(f"❌ Failed to update Airtable for: {title}\n")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {title}: {str(e)}\n")
                self.airtable.mark_as_error(record_id, str(e))
    
    def run_once(self):
        """Run one processing cycle."""
        try:
            self.process_pending_videos()
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
    
    def run_forever(self):
        """Run continuously, polling for new videos."""
        logger.info(f"🚀 Poker Video Processor Service Started")
        logger.info(f"📊 Base: {os.getenv('AIRTABLE_BASE_ID')}")
        logger.info(f"📋 Table: {os.getenv('AIRTABLE_TABLE_ID')}")
        logger.info(f"⏱️  Poll interval: {self.poll_interval} seconds")
        logger.info(f"{'='*60}\n")
        
        while True:
            try:
                self.process_pending_videos()
                logger.info(f"💤 Sleeping for {self.poll_interval} seconds...\n")
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Service stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info(f"Retrying in {self.poll_interval} seconds...")
                time.sleep(self.poll_interval)


def main():
    """Entry point for the service."""
    import sys
    
    service = PokerVideoService()
    
    # Check if running in one-shot mode
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        logger.info("Running in one-shot mode")
        service.run_once()
    else:
        service.run_forever()


if __name__ == "__main__":
    main()
