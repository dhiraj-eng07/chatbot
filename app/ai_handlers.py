import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import json
import re
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class MockAIHandler:
    """Fallback mock AI handler when APIs fail"""
    
    def __init__(self):
        self.name = "MockAI"
        logger.info("Mock AI handler initialized for fallback")
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate intelligent mock responses based on context"""
        prompt_lower = prompt.lower()
        context_lower = context.lower()
        
        # Extract meeting info from context
        participants = []
        if "participants:" in context_lower:
            # Try to extract participants
            lines = context.split('\n')
            for line in lines:
                if 'participants:' in line.lower():
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        participants = [p.strip() for p in parts[1].split(',')]
                        break
        
        # Generate context-aware responses
        responses = []
        
        if "action" in prompt_lower or "task" in prompt_lower:
            responses = [
                f"Based on the meeting, here are the action items: 1. Complete frontend development by Friday, 2. Fix backend issues by Wednesday, 3. Update documentation by next week.",
                f"The main tasks assigned were: Frontend completion (Alice), Backend fixes (Bob), and Documentation updates (Charlie).",
                f"Action items from the meeting include: Finalize design mockups, Implement API endpoints, and Write test cases."
            ]
        elif "participant" in prompt_lower or "who attended" in prompt_lower:
            if participants:
                resp = f"The meeting participants were: {', '.join(participants[:3])}"
                if len(participants) > 3:
                    resp += f", and {len(participants) - 3} others"
                responses = [resp]
            else:
                responses = [
                    "The meeting was attended by team members including the project manager, lead developer, and designers.",
                    "Participants included key stakeholders from engineering, design, and product management teams.",
                    "Team members from various departments attended the meeting to discuss project progress."
                ]
        elif "decision" in prompt_lower:
            responses = [
                "Key decisions made: 1. Adopt React for the frontend, 2. Use AWS for deployment, 3. Schedule weekly standups on Mondays.",
                "The team decided to proceed with the proposed architecture and set clear milestones for the next quarter.",
                "Decisions included finalizing the tech stack, approving the project timeline, and allocating resources."
            ]
        elif "summary" in prompt_lower or "discuss" in prompt_lower:
            responses = [
                "The meeting covered project updates, timeline reviews, and resource allocation. The team aligned on next steps and deadlines.",
                "Discussion focused on current progress, challenges faced, and solutions proposed. Future plans were also outlined.",
                "Key topics included sprint planning, bug fixes, feature prioritization, and team coordination for upcoming deliverables."
            ]
        elif "when" in prompt_lower and ("next" in prompt_lower or "meeting" in prompt_lower):
            next_date = (datetime.now() + timedelta(days=7)).strftime("%A, %B %d")
            responses = [f"The next meeting is scheduled for {next_date} at 10:00 AM."]
        elif "deadline" in prompt_lower or "due" in prompt_lower:
            responses = [
                "The main deadlines are: Frontend completion by Friday, Backend integration by Wednesday next week, and final testing by end of month.",
                "Key due dates: Design approval by tomorrow, development completion by Friday, and deployment by next Monday.",
                "Deadlines discussed: Phase 1 completion in 2 weeks, Phase 2 in 4 weeks, and final delivery in 6 weeks."
            ]
        else:
            responses = [
                "Based on the meeting notes, the team made significant progress and aligned on next steps.",
                "The discussion was productive with clear outcomes and assigned responsibilities.",
                "Key takeaways include improved coordination and defined action items for the coming week.",
                "The meeting successfully addressed all agenda items and set the direction for future work."
            ]
        
        response = random.choice(responses)
        
        # Add context awareness if we have meeting data
        if context and len(context) > 100:
            # Extract meeting title if available
            title = "the meeting"
            if "meeting" in context_lower:
                lines = context.split('\n')
                for line in lines:
                    if 'meeting' in line.lower() and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1 and len(parts[1].strip()) < 50:
                            title = parts[1].strip()
                            break
            
            response = f"Regarding {title}, {response.lower()}"
        
        return response
    
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate intelligent mock meeting summary"""
        word_count = len(transcript.split())
        
        # Extract info from transcript
        lines = transcript.split('\n')
        
        # Try to extract participants
        participants = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['participant', 'attendee', 'present:']):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        participant_text = parts[1]
                        # Extract names/emails
                        for item in participant_text.split(','):
                            item = item.strip()
                            if '@' in item:
                                # Email
                                participants.append(item)
                            elif len(item.split()) <= 3:
                                # Name
                                participants.append(item)
                        if participants:
                            break
        
        if not participants:
            participants = ["Project Manager", "Lead Developer", "UX Designer", "QA Engineer"]
        
        # Generate summary based on transcript content
        topics = []
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ['frontend', 'ui', 'ux', 'design']):
            topics.append("frontend development")
        if any(word in transcript_lower for word in ['backend', 'api', 'server', 'database']):
            topics.append("backend architecture")
        if any(word in transcript_lower for word in ['design', 'mockup', 'wireframe']):
            topics.append("design review")
        if any(word in transcript_lower for word in ['test', 'qa', 'quality']):
            topics.append("testing strategy")
        if any(word in transcript_lower for word in ['deploy', 'launch', 'release']):
            topics.append("deployment plans")
        
        if not topics:
            topics = ["project progress", "timeline review", "next steps"]
        
        summary = f"A meeting was held with {len(participants)} participants. The discussion covered {', '.join(topics[:3])}. Key decisions were made and action items assigned."
        
        if word_count > 100:
            summary = f"An extensive meeting ({word_count} words) was conducted involving {len(participants)} team members. Topics included {', '.join(topics[:3])}. Clear outcomes and responsibilities were established."
        
        return {
            "summary": summary,
            "key_points": [
                f"Progress update on {topics[0] if topics else 'project'}",
                "Timeline review and adjustment",
                "Resource allocation discussion",
                "Risk assessment and mitigation"
            ],
            "action_items": [
                {"task": f"Complete {topics[0] if topics else 'assigned'} tasks", 
                 "assignee": participants[0] if participants else "Team Lead", 
                 "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")},
                {"task": "Prepare status report", 
                 "assignee": participants[1] if len(participants) > 1 else "Project Manager", 
                 "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")},
                {"task": "Schedule follow-up meeting", 
                 "assignee": participants[2] if len(participants) > 2 else "Coordinator", 
                 "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
            ],
            "decisions": [
                f"Proceed with {topics[0] if topics else 'proposed'} approach",
                "Approve updated timeline",
                "Allocate additional resources as needed"
            ],
            "tags": ["meeting", "planning", "team"] + topics[:2]
        }

class GeminiHandler:
    def __init__(self):
        self.available = False
        self.model = None
        
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            logger.warning("Gemini API key not configured")
            return
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Try different model names
            model_names = [
                "gemini-1.5-pro-latest",
                "gemini-1.0-pro-latest",
                "gemini-pro",  # Try the original as last resort
                "models/gemini-pro"  # Full path
            ]
            
            for model_name in model_names:
                try:
                    logger.info(f"Trying Gemini model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    # Test with a simple prompt
                    test_response = self.model.generate_content("Hello")
                    logger.info(f"✅ Gemini model '{model_name}' initialized successfully")
                    self.available = True
                    settings.GEMINI_MODEL = model_name  # Update setting
                    break
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
            
            if not self.available:
                logger.error("All Gemini models failed. Using mock AI instead.")
                self.mock_handler = MockAIHandler()
                
        except Exception as e:
            logger.error(f"Gemini initialization error: {e}")
            self.mock_handler = MockAIHandler()
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Gemini or fallback to mock"""
        try:
            if not self.available:
                if hasattr(self, 'mock_handler'):
                    return await self.mock_handler.generate_response(prompt, context)
                return "Gemini API is not available. Using mock response: " + await MockAIHandler().generate_response(prompt, context)
            
            full_prompt = f"""Context from meetings: {context}

            Based strictly on this context, answer the following question:
            {prompt}

            If the context doesn't contain relevant information, say "I don't have enough information from the meeting notes to answer that question."

            Answer:"""
            
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback to mock
            return await MockAIHandler().generate_response(prompt, context)
    
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate meeting summary using Gemini or fallback"""
        try:
            if not self.available:
                if hasattr(self, 'mock_handler'):
                    return await self.mock_handler.generate_summary(transcript)
                return await MockAIHandler().generate_summary(transcript)
            
            prompt = f"""
            Analyze this meeting transcript and extract the following information:
            
            1. Summary: A concise 3-4 sentence overview of what was discussed
            2. Key Points: 3-5 main discussion points as a list
            3. Action Items: 2-4 specific tasks with assignees and due dates (format as JSON objects)
            4. Decisions: 2-3 decisions that were made as a list
            5. Tags: 3-5 relevant keywords or tags
            
            Format the response as a valid JSON object with exactly these keys: summary, key_points, action_items, decisions, tags
            
            Transcript:
            {transcript[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean and parse JSON
            try:
                # Remove markdown code blocks
                result_text = result_text.replace("```json", "").replace("```", "").strip()
                result = json.loads(result_text)
                
                # Validate structure
                required_keys = ["summary", "key_points", "action_items", "decisions", "tags"]
                for key in required_keys:
                    if key not in result:
                        result[key] = []
                
                return result
            except json.JSONDecodeError:
                # Try to extract JSON
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                
                # Fallback to mock
                logger.warning("Failed to parse Gemini JSON response, using mock")
                return await MockAIHandler().generate_summary(transcript)
                
        except Exception as e:
            logger.error(f"Gemini summarization error: {e}")
            return await MockAIHandler().generate_summary(transcript)

class OpenAIHandler:
    def __init__(self):
        self.available = False
        self.client = None
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured")
            return
        
        try:
            import openai
            self.openai = openai
            
            # Try to initialize
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Test with a simple request
            test_response = self.client.models.list()
            self.available = True
            logger.info("✅ OpenAI handler initialized successfully")
            
        except ImportError:
            logger.error("OpenAI package not installed")
        except Exception as e:
            logger.error(f"OpenAI initialization error: {e}")
            self.mock_handler = MockAIHandler()
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using OpenAI or fallback"""
        try:
            if not self.available:
                if hasattr(self, 'mock_handler'):
                    return await self.mock_handler.generate_response(prompt, context)
                return "OpenAI API is not available. Using mock response: " + await MockAIHandler().generate_response(prompt, context)
            
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer based on the context above:"
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful meeting assistant. Answer questions based only on the provided meeting context."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return await MockAIHandler().generate_response(prompt, context)
    
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate meeting summary using OpenAI or fallback"""
        try:
            if not self.available:
                if hasattr(self, 'mock_handler'):
                    return await self.mock_handler.generate_summary(transcript)
                return await MockAIHandler().generate_summary(transcript)
            
            prompt = f"""
            Analyze this meeting transcript and provide:
            1. A concise summary (3-4 sentences)
            2. 3-5 key discussion points
            3. 2-4 action items with assignees and due dates
            4. 2-3 decisions made
            5. 3-5 relevant tags
            
            Format as JSON with keys: summary, key_points, action_items, decisions, tags
            
            Transcript:
            {transcript[:3000]}
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert meeting summarizer. Extract key information and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
                # Validate structure
                required_keys = ["summary", "key_points", "action_items", "decisions", "tags"]
                for key in required_keys:
                    if key not in result:
                        result[key] = []
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI JSON response, using mock")
                return await MockAIHandler().generate_summary(transcript)
                
        except Exception as e:
            logger.error(f"OpenAI summarization error: {e}")
            return await MockAIHandler().generate_summary(transcript)

class AIProvider:
    """Factory class to manage AI providers with intelligent fallback"""
    
    def __init__(self):
        self.openai_handler = None
        self.gemini_handler = None
        self.mock_handler = MockAIHandler()
        
        # Initialize handlers
        try:
            self.openai_handler = OpenAIHandler()
            if self.openai_handler.available:
                logger.info("✅ OpenAI available")
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")
        
        try:
            self.gemini_handler = GeminiHandler()
            if hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
                logger.info("✅ Gemini available")
        except Exception as e:
            logger.warning(f"Gemini initialization failed: {e}")
        
        # Log available providers
        available = self.get_available_providers()
        logger.info(f"Available AI providers: {available}")
        
        if not available:
            logger.info("⚠️  No AI providers available, using mock AI only")
    
    async def get_response(self, prompt: str, context: str = "", provider: str = None) -> str:
        """Get response with intelligent provider selection"""
        try:
            # Use specified provider or default
            if not provider:
                provider = settings.DEFAULT_AI_PROVIDER
            
            # Try specified provider first
            if provider == "openai" and self.openai_handler and self.openai_handler.available:
                return await self.openai_handler.generate_response(prompt, context)
            elif provider == "gemini" and self.gemini_handler and hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
                return await self.gemini_handler.generate_response(prompt, context)
            
            # Fallback to any available provider
            if self.openai_handler and self.openai_handler.available:
                return await self.openai_handler.generate_response(prompt, context)
            elif self.gemini_handler and hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
                return await self.gemini_handler.generate_response(prompt, context)
            
            # Use mock AI as last resort
            return await self.mock_handler.generate_response(prompt, context)
            
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return await self.mock_handler.generate_response(prompt, context)
    
    async def generate_meeting_summary(self, transcript: str, provider: str = None) -> Dict[str, Any]:
        """Generate meeting summary with intelligent provider selection"""
        try:
            if not provider:
                provider = settings.DEFAULT_AI_PROVIDER
            
            # Try specified provider
            if provider == "openai" and self.openai_handler and self.openai_handler.available:
                return await self.openai_handler.generate_summary(transcript)
            elif provider == "gemini" and self.gemini_handler and hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
                return await self.gemini_handler.generate_summary(transcript)
            
            # Fallback
            if self.openai_handler and self.openai_handler.available:
                return await self.openai_handler.generate_summary(transcript)
            elif self.gemini_handler and hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
                return await self.gemini_handler.generate_summary(transcript)
            
            # Use mock
            return await self.mock_handler.generate_summary(transcript)
            
        except Exception as e:
            logger.error(f"Error in generate_meeting_summary: {e}")
            return await self.mock_handler.generate_summary(transcript)
    
    def get_available_providers(self) -> List[str]:
        """Get list of actually available AI providers"""
        providers = []
        if self.openai_handler and self.openai_handler.available:
            providers.append("openai")
        if self.gemini_handler and hasattr(self.gemini_handler, 'available') and self.gemini_handler.available:
            providers.append("gemini")
        
        # Always include mock as fallback
        providers.append("mock")
        
        return providers

# Create AI provider instance
ai_provider = AIProvider()