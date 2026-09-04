from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()

ai_key = api_key=os.getenv("GROQ_API_KEY")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Groq configuration
    GROQ_API_KEY: str = ai_key
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1024

    # System prompt for chatbot
    SYSTEM_PROMPT: str = (
        "Você é um assistente virtual prestativo, educado e ágil no WhatsApp. "
        "Responda sempre em português do Brasil de forma clara e natural. "
        "Seja direto e amigável."
    )

    # WAHA API configuration
    WAHA_API_URL: str = "http://waha:3000"
    WAHA_API_KEY: Optional[str] = None
    WAHA_SESSION: str = "default"

    # Bot behavior configuration
    IGNORE_GROUPS: bool = True
    MAX_HISTORY_MESSAGES: int = 12
    BOT_PORT: int = 8000
    BOT_HOST: str = "0.0.0.0"


settings = Settings()
