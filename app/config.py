import os
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "meeting_chatbot")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
    
    # Application Configuration
    DEFAULT_AI_PROVIDER: Literal["openai", "gemini", "mock"] = os.getenv("DEFAULT_AI_PROVIDER", "mock")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1000))
    
    class Config:
        env_file = ".env"

settings = Settings()