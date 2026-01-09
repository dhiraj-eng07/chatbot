from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from bson import ObjectId
from datetime import datetime, timedelta
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None
    meeting_summaries = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            self.meeting_summaries = self.database.meeting_summaries
            
            # Create indexes
            await self.create_indexes()
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create necessary indexes"""
        indexes = [
            IndexModel([("meeting_id", ASCENDING)], unique=True),
            IndexModel([("title", TEXT)]),
            IndexModel([("date", DESCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("participants", ASCENDING)]),
        ]
        await self.meeting_summaries.create_indexes(indexes)
    
    async def insert_meeting_summary(self, meeting_data: dict) -> str:
        """Insert a new meeting summary"""
        try:
            # Convert datetime objects to string format for MongoDB
            for key, value in meeting_data.items():
                if isinstance(value, datetime):
                    meeting_data[key] = value.isoformat()
            
            result = await self.meeting_summaries.insert_one(meeting_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting meeting summary: {e}")
            raise
    
    async def get_meeting_by_id(self, meeting_id: str) -> dict:
        """Get meeting summary by meeting_id"""
        try:
            meeting = await self.meeting_summaries.find_one({"meeting_id": meeting_id})
            
            # Convert ObjectId to string for JSON serialization
            if meeting and '_id' in meeting:
                meeting['_id'] = str(meeting['_id'])
            
            return meeting
        except Exception as e:
            logger.error(f"Error fetching meeting: {e}")
            return None
    
    async def search_meetings(self, query: dict, limit: int = 10) -> list:
        """Search for meetings based on query"""
        try:
            cursor = self.meeting_summaries.find(query).limit(limit)
            meetings = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            for meeting in meetings:
                if '_id' in meeting:
                    meeting['_id'] = str(meeting['_id'])
            
            return meetings
        except Exception as e:
            logger.error(f"Error searching meetings: {e}")
            return []
    
    async def get_recent_meetings(self, days: int = 7, limit: int = 20) -> list:
        """Get recent meetings from the last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = {"date": {"$gte": cutoff_date.isoformat()}}
            
            cursor = self.meeting_summaries.find(query).sort("date", DESCENDING).limit(limit)
            meetings = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            for meeting in meetings:
                if '_id' in meeting:
                    meeting['_id'] = str(meeting['_id'])
            
            return meetings
        except Exception as e:
            logger.error(f"Error fetching recent meetings: {e}")
            return []
    
    async def update_meeting_summary(self, meeting_id: str, update_data: dict) -> bool:
        """Update an existing meeting summary"""
        try:
            # Convert datetime objects
            for key, value in update_data.items():
                if isinstance(value, datetime):
                    update_data[key] = value.isoformat()
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = await self.meeting_summaries.update_one(
                {"meeting_id": meeting_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating meeting: {e}")
            return False
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting summary"""
        try:
            result = await self.meeting_summaries.delete_one({"meeting_id": meeting_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting meeting: {e}")
            return False

# Create database instance
db = Database()