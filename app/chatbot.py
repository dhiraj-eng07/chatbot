from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from app.ai_handlers import ai_provider
from app.database import db
from app.models import ChatQuery, ChatResponse

logger = logging.getLogger(__name__)

class MeetingChatbot:
    def __init__(self):
        self.ai_provider = ai_provider
    
    async def _build_context(self, query: ChatQuery) -> str:
        """
        Build context from relevant meetings based on the query
        """
        try:
            # If specific meeting ID is provided
            if query.meeting_id:
                meeting = await db.get_meeting_by_id(query.meeting_id)
                if meeting:
                    return self._format_meeting_context([meeting])
            
            # Search for relevant meetings
            relevant_meetings = await self._find_relevant_meetings(query)
            
            if not relevant_meetings:
                # Fallback to recent meetings
                relevant_meetings = await db.get_recent_meetings(days=query.context_days or 7)
            
            return self._format_meeting_context(relevant_meetings)
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return ""
    
    async def _find_relevant_meetings(self, query: ChatQuery) -> List[Dict[str, Any]]:
        """
        Find meetings relevant to the query
        """
        try:
            # Simple keyword matching for now
            # You can enhance this with embeddings/semantic search
            import re
            
            # Extract potential keywords from query
            keywords = re.findall(r'\b\w+\b', query.question.lower())
            
            # Search in recent meetings
            recent_meetings = await db.get_recent_meetings(days=query.context_days or 30, limit=50)
            
            relevant_meetings = []
            for meeting in recent_meetings:
                # Check if keywords appear in meeting content
                content = f"{meeting.get('title', '')} {meeting.get('summary', '')} {' '.join(meeting.get('tags', []))}"
                content_lower = content.lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                
                if matches > 0:
                    meeting['relevance_score'] = matches / len(keywords) if keywords else 0
                    relevant_meetings.append(meeting)
            
            # Sort by relevance score
            relevant_meetings.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return relevant_meetings[:10]  # Return top 10 relevant meetings
            
        except Exception as e:
            logger.error(f"Error finding relevant meetings: {e}")
            return []
    
    def _format_meeting_context(self, meetings: List[Dict[str, Any]]) -> str:
        """
        Format meetings into a context string
        """
        if not meetings:
            return "No meeting data available."
        
        context_parts = []
        
        for i, meeting in enumerate(meetings, 1):
            context = f"""
            Meeting {i}: {meeting.get('title', 'Untitled')}
            Date: {meeting.get('date', 'Unknown')}
            Participants: {', '.join(meeting.get('participants', []))}
            Summary: {meeting.get('summary', 'No summary available')}
            Key Points: {', '.join(meeting.get('key_points', []))}
            Action Items: {self._format_action_items(meeting.get('action_items', []))}
            Decisions: {', '.join(meeting.get('decisions', []))}
            """
            context_parts.append(context.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    def _format_action_items(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items for context"""
        if not action_items:
            return "No action items"
        
        formatted = []
        for item in action_items:
            task = item.get('task', 'Unknown task')
            assignee = item.get('assignee', 'Unassigned')
            due_date = item.get('due_date', 'No due date')
            formatted.append(f"{task} (Assigned to: {assignee}, Due: {due_date})")
        
        return "; ".join(formatted)
    
    async def ask_question(self, query: ChatQuery) -> ChatResponse:
        """
        Main method to answer questions about meetings
        """
        try:
            # Validate AI provider
            available_providers = self.ai_provider.get_available_providers()
            if query.ai_provider not in available_providers:
                query.ai_provider = available_providers[0] if available_providers else "openai"
            
            # Build context from meetings
            context = await self._build_context(query)
            
            if not context or context == "No meeting data available.":
                # If no context, provide generic response
                answer = "I don't have access to any meeting data. Please upload meeting transcripts first."
                return ChatResponse(
                    answer=answer,
                    sources=[],
                    ai_provider=query.ai_provider,
                    confidence=0.0
                )
            
            # Generate answer using AI
            answer = await self.ai_provider.get_response(
                prompt=query.question,
                context=context,
                provider=query.ai_provider
            )
            
            # Calculate confidence (simplified - can be enhanced)
            confidence = self._calculate_confidence(answer, query.question)
            
            # Get source meetings
            sources = await self._get_source_meetings(query)
            
            return ChatResponse(
                answer=answer,
                sources=sources,
                ai_provider=query.ai_provider,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return ChatResponse(
                answer=f"Error processing your question: {str(e)}",
                sources=[],
                ai_provider=query.ai_provider or "openai",
                confidence=0.0
            )
    
    def _calculate_confidence(self, answer: str, question: str) -> float:
        """
        Calculate confidence score for the answer
        """
        # Simple confidence calculation
        # You can enhance this with more sophisticated methods
        
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # Check for uncertainty indicators
        uncertainty_phrases = [
            "i don't know", "i'm not sure", "no information",
            "not mentioned", "not specified", "not available"
        ]
        
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                return 0.2
        
        # Check if answer contains relevant terms from question
        question_terms = set(question_lower.split())
        answer_terms = set(answer_lower.split())
        
        overlap = len(question_terms.intersection(answer_terms))
        if question_terms:
            term_similarity = overlap / len(question_terms)
        else:
            term_similarity = 0
        
        # Base confidence
        base_confidence = 0.7
        
        # Adjust based on term similarity
        confidence = min(0.95, base_confidence + (term_similarity * 0.3))
        
        return round(confidence, 2)
    
    async def _get_source_meetings(self, query: ChatQuery) -> List[Dict[str, Any]]:
        """
        Get source meetings that contributed to the answer
        """
        try:
            if query.meeting_id:
                meeting = await db.get_meeting_by_id(query.meeting_id)
                return [self._format_source_meeting(meeting)] if meeting else []
            else:
                meetings = await self._find_relevant_meetings(query)
                return [self._format_source_meeting(m) for m in meetings[:3]]
        except Exception as e:
            logger.error(f"Error getting source meetings: {e}")
            return []
    
    def _format_source_meeting(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Format meeting for source display"""
        return {
            "meeting_id": meeting.get("meeting_id"),
            "title": meeting.get("title"),
            "date": meeting.get("date"),
            "summary": meeting.get("summary", "")[:200] + "..." if len(meeting.get("summary", "")) > 200 else meeting.get("summary", "")
        }

# Create chatbot instance
chatbot = MeetingChatbot()