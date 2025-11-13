"""
Airtable Client - Using pure requests library (no pyairtable)
Handles polling for new records and updating with results.
"""

import logging
import os
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AirtableClient:
    """Manages Airtable operations for poker content using REST API."""
    
    def __init__(self, api_key: str, base_id: str, table_id: str):
        self.api_key = api_key
        self.base_id = base_id
        self.table_id = table_id
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info("✅ Airtable client initialized")
        
    def get_pending_videos(self) -> List[Dict]:
        """
        Get all videos with Status = 'Raw' that need processing.
        
        Returns:
            List of records with id, fields, and createdTime
        """
        try:
            # Use filterByFormula to get records with Status = 'Raw'
            formula = "{Status}='Raw'"
            params = {
                "filterByFormula": formula,
                "maxRecords": 100
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            records = data.get('records', [])
            
            # Filter to only those with a video URL
            pending = [
                r for r in records 
                if r['fields'].get('Source File/Link')
            ]
            
            logger.info(f"Found {len(pending)} pending videos")
            return pending
            
        except requests.exceptions.RequestException as e:
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
            
            url = f"{self.base_url}/{record_id}"
            payload = {"fields": airtable_updates}
            
            response = requests.patch(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"✅ Updated record {record_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error updating record {record_id}: {e}")
            return False
    
    def mark_as_processing(self, record_id: str) -> bool:
        """Mark a record as being processed to avoid duplicate processing."""
        try:
            url = f"{self.base_url}/{record_id}"
            payload = {"fields": {"Status": "Processing"}}
            
            response = requests.patch(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking as processing: {e}")
            return False
    
    def mark_as_error(self, record_id: str, error_msg: str) -> bool:
        """Mark a record as having an error."""
        try:
            url = f"{self.base_url}/{record_id}"
            payload = {"fields": {
                "Status": "Raw",
                "Core Philosophy": f"ERROR: {error_msg}"
            }}
            
            response = requests.patch(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking as error: {e}")
            return False
