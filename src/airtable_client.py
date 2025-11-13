"""
Airtable Client
Handles polling for new records and updating with results.
"""

import logging
from typing import List, Dict, Optional
from pyairtable import Api
from pyairtable.formulas import match

logger = logging.getLogger(__name__)


class AirtableClient:
    """Manages Airtable operations for poker content."""
    
    def __init__(self, api_key: str, base_id: str, table_id: str):
        self.api = Api(api_key)
        self.base_id = base_id
        self.table_id = table_id
        self.table = self.api.table(base_id, table_id)
        
    def get_pending_videos(self) -> List[Dict]:
        """
        Get all videos with Status = 'Raw' that need processing.
        
        Returns:
            List of records with id, fields, and createdTime
        """
        try:
            # Use formula to filter for Raw status
            formula = match({"Status": "Raw"})
            records = self.table.all(formula=formula)
            
            # Filter to only those with a video URL
            pending = [
                r for r in records 
                if r['fields'].get('Source File/Link')
            ]
            
            logger.info(f"Found {len(pending)} pending videos")
            return pending
            
        except Exception as e:
            logger.error(f"Error fetching pending videos: {e}")
            return []
    
    def update_record(self, record_id: str, updates: Dict) -> bool:
        """
        Update a record with processing results.
        
        Args:
            record_id: The Airtable record ID
            updates: Dict of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Map our field names to Airtable field names
            field_mapping = {
                "transcription": "Core Philosophy",  # Store full transcription here
                "key_quotes": "Key Quotes",
                "core_philosophy": "Core Philosophy",
                "status": "Status"
            }
            
            airtable_updates = {}
            for key, value in updates.items():
                if key in field_mapping and value:
                    airtable_updates[field_mapping[key]] = value
            
            self.table.update(record_id, airtable_updates)
            logger.info(f"✅ Updated record {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating record {record_id}: {e}")
            return False
    
    def mark_as_processing(self, record_id: str) -> bool:
        """Mark a record as being processed to avoid duplicate processing."""
        try:
            self.table.update(record_id, {"Status": "Processing"})
            return True
        except Exception as e:
            logger.error(f"Error marking as processing: {e}")
            return False
    
    def mark_as_error(self, record_id: str, error_msg: str) -> bool:
        """Mark a record as having an error."""
        try:
            self.table.update(record_id, {
                "Status": "Raw",
                "Core Philosophy": f"ERROR: {error_msg}"
            })
            return True
        except Exception as e:
            logger.error(f"Error marking as error: {e}")
            return False
