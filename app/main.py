from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import json
from datetime import datetime
import logging

from app.config import settings
from app.database import db
from app.models import MeetingSummary, ChatQuery, ChatResponse, MeetingUpload, MeetingUpdate
from app.summary_generator import SummaryGenerator
from app.chatbot import chatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    logger.info("Application started")
    yield
    # Shutdown
    await db.disconnect()
    logger.info("Application shutdown")

app = FastAPI(
    title="Meeting Summary Chatbot API",
    description="Agentic Chatbot for Meeting Summaries with Dual AI Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Meeting Summary Chatbot API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        # Try to ping MongoDB
        await db.client.admin.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "ai_providers": chatbot.ai_provider.get_available_providers() if hasattr(chatbot, 'ai_provider') else []
    }

# Meeting endpoints
@app.post("/meetings/upload")
async def upload_meeting(
    upload_data: MeetingUpload = Body(...)
):
    """
    Upload meeting transcript and generate summary
    """
    try:
        metadata = {
            "title": upload_data.title,
            "participants": upload_data.participants,
            "duration_minutes": upload_data.duration_minutes,
            "date": datetime.now().isoformat()
        }
        
        # Generate and store summary
        meeting_data = await SummaryGenerator.generate_and_store_summary(
            transcript=upload_data.transcript,
            metadata=metadata,
            ai_provider_name=upload_data.ai_provider
        )
        
        return {
            "message": "Meeting summary generated successfully",
            "meeting_id": meeting_data["meeting_id"],
            "data": meeting_data
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meetings/upload-form")
async def upload_meeting_form(
    transcript: str = Form(..., description="Meeting transcript"),
    title: str = Form("Untitled Meeting"),
    participants: str = Form("[]"),
    duration_minutes: int = Form(60),
    ai_provider: str = Form("openai")
):
    """
    Upload meeting transcript via form data
    """
    try:
        # Parse participants
        try:
            participants_list = json.loads(participants)
        except:
            participants_list = []
        
        metadata = {
            "title": title,
            "participants": participants_list,
            "duration_minutes": duration_minutes,
            "date": datetime.now().isoformat()
        }
        
        # Generate and store summary
        meeting_data = await SummaryGenerator.generate_and_store_summary(
            transcript=transcript,
            metadata=metadata,
            ai_provider_name=ai_provider
        )
        
        return {
            "message": "Meeting summary generated successfully",
            "meeting_id": meeting_data["meeting_id"],
            "data": meeting_data
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    """
    Get meeting summary by ID
    """
    meeting = await db.get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@app.get("/meetings")
async def list_meetings(
    limit: int = 20,
    offset: int = 0,
    tag: Optional[str] = None,
    participant: Optional[str] = None
):
    """
    List all meetings with optional filters
    """
    query = {}
    if tag:
        query["tags"] = tag
    if participant:
        query["participants"] = participant
    
    meetings = await db.search_meetings(query, limit=limit)
    return meetings

@app.put("/meetings/{meeting_id}")
async def update_meeting(
    meeting_id: str,
    update_data: MeetingUpdate = Body(...)
):
    """
    Update meeting transcript and regenerate summary
    """
    try:
        update_payload = {}
        if update_data.transcript:
            update_payload["transcript"] = update_data.transcript
        if update_data.metadata:
            update_payload.update(update_data.metadata)
        
        success = await SummaryGenerator.update_meeting_summary(
            meeting_id=meeting_id,
            transcript=update_data.transcript,
            metadata=update_data.metadata,
            ai_provider_name=update_data.ai_provider
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Meeting not found or update failed")
        
        return {"message": "Meeting updated successfully"}
        
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """
    Delete a meeting
    """
    success = await db.delete_meeting(meeting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"message": "Meeting deleted successfully"}

# Chatbot endpoints
@app.post("/chat/ask", response_model=ChatResponse)
async def ask_question(query: ChatQuery):
    """
    Ask a question about meetings
    """
    try:
        response = await chatbot.ask_question(query)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/providers")
async def get_ai_providers():
    """
    Get available AI providers
    """
    if hasattr(chatbot, 'ai_provider'):
        providers = chatbot.ai_provider.get_available_providers()
    else:
        providers = ["openai", "gemini"]  # Default
    return {"available_providers": providers}

# Search endpoints
@app.get("/search")
async def search_meetings(
    q: str,
    limit: int = 10,
    days: int = 30
):
    """
    Search meetings by keyword
    """
    # Get recent meetings
    meetings = await db.get_recent_meetings(days=days, limit=50)
    
    # Simple keyword search
    results = []
    search_terms = q.lower().split()
    
    for meeting in meetings:
        content = f"{meeting.get('title', '')} {meeting.get('summary', '')}"
        content_lower = content.lower()
        
        # Check if any search terms appear
        if any(term in content_lower for term in search_terms):
            results.append({
                "meeting_id": meeting.get("meeting_id"),
                "title": meeting.get("title"),
                "date": meeting.get("date"),
                "summary_preview": meeting.get("summary", "")[:100] + "..." if len(meeting.get("summary", "")) > 100 else meeting.get("summary", "")
            })
    
    return {"query": q, "results": results[:limit]}

@app.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API is working
    """
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)