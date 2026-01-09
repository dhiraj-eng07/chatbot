from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.ai_handlers import ai_provider
from app.database import db

logger = logging.getLogger(__name__)

class SummaryGenerator:
    @staticmethod
    async def generate_and_store_summary(
        transcript: str,
        metadata: Dict[str, Any],
        ai_provider_name: str = "openai"
    ) -> Dict[str, Any]:
        """
        Generate meeting summary from transcript and store in database
        """
        try:
            # Generate summary using AI
            logger.info(f"Generating summary using {ai_provider_name}")
            ai_result = await ai_provider.generate_meeting_summary(transcript, ai_provider_name)
            
            # Prepare meeting data
            meeting_data = {
                "meeting_id": metadata.get("meeting_id", f"MTG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                "title": metadata.get("title", "Untitled Meeting"),
                "participants": metadata.get("participants", []),
                "date": metadata.get("date", datetime.now()),
                "duration_minutes": metadata.get("duration_minutes", 0),
                "transcript": transcript,
                "summary": ai_result.get("summary", ""),
                "key_points": ai_result.get("key_points", []),
                "action_items": ai_result.get("action_items", []),
                "decisions": ai_result.get("decisions", []),
                "tags": ai_result.get("tags", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Store in database
            meeting_id = await db.insert_meeting_summary(meeting_data)
            meeting_data["_id"] = str(meeting_id)
            
            logger.info(f"Successfully stored meeting: {meeting_data['meeting_id']}")
            return meeting_data
            
        except Exception as e:
            logger.error(f"Error generating/saving summary: {e}")
            raise
    
    @staticmethod
    async def update_meeting_summary(
        meeting_id: str,
        transcript: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ai_provider_name: str = "openai"
    ) -> bool:
        """
        Update existing meeting summary with new transcript or metadata
        """
        try:
            update_data = {}
            
            if transcript:
                # Regenerate summary with new transcript
                ai_result = await ai_provider.generate_meeting_summary(transcript, ai_provider_name)
                update_data.update({
                    "transcript": transcript,
                    "summary": ai_result.get("summary", ""),
                    "key_points": ai_result.get("key_points", []),
                    "action_items": ai_result.get("action_items", []),
                    "decisions": ai_result.get("decisions", []),
                    "tags": ai_result.get("tags", [])
                })
            
            if metadata:
                update_data.update(metadata)
            
            if update_data:
                update_data["updated_at"] = datetime.now()
                success = await db.update_meeting_summary(meeting_id, update_data)
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating meeting summary: {e}")
            return False