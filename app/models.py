from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from pymongo import IndexModel, ASCENDING
from pydantic_core import core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        return core_schema.str_schema()

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

class MeetingSummary(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    meeting_id: str = Field(..., description="Unique identifier for the meeting")
    title: str = Field(..., description="Meeting title")
    participants: List[str] = Field(default=[], description="List of participants")
    date: datetime = Field(default_factory=datetime.now, description="Meeting date")
    duration_minutes: int = Field(..., description="Meeting duration in minutes")
    transcript: str = Field(..., description="Full meeting transcript")
    summary: str = Field(..., description="AI-generated summary")
    key_points: List[str] = Field(default=[], description="Key discussion points")
    action_items: List[Dict[str, Any]] = Field(default=[], description="Action items with assignees")
    decisions: List[str] = Field(default=[], description="Decisions made")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "meeting_id": "MTG-2023-001",
                "title": "Project Kickoff",
                "participants": ["john@example.com", "jane@example.com"],
                "duration_minutes": 60,
                "summary": "Project kickoff meeting discussing scope and timelines...",
                "key_points": ["Scope finalization", "Timeline approval"],
                "action_items": [{"task": "Prepare requirements", "assignee": "john", "due_date": "2023-12-31"}]
            }
        }
    )

class ChatQuery(BaseModel):
    question: str = Field(..., description="User's question about the meeting")
    meeting_id: Optional[str] = Field(None, description="Specific meeting ID to query")
    ai_provider: str = Field("openai", description="AI provider to use (openai or gemini)")
    context_days: Optional[int] = Field(7, description="Number of days to look back for context")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source meeting information")
    ai_provider: str = Field(..., description="AI provider used")
    confidence: float = Field(..., description="Confidence score of the answer")

class MeetingUpload(BaseModel):
    transcript: str = Field(..., description="Meeting transcript")
    title: str = Field("Untitled Meeting", description="Meeting title")
    participants: List[str] = Field(default=[], description="List of participants")
    duration_minutes: int = Field(60, description="Meeting duration in minutes")
    ai_provider: str = Field("openai", description="AI provider to use for summarization")

class MeetingUpdate(BaseModel):
    transcript: Optional[str] = Field(None, description="Updated transcript")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    ai_provider: str = Field("openai", description="AI provider to use for re-summarization")