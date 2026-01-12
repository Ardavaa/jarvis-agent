"""
Configuration management for JARVIS
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    # Application
    app_name: str = "JARVIS"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout: int = 120
    
    # Database Configuration
    database_url: str = "sqlite:///./jarvis.db"
    vector_db_path: str = "./chroma_db"
    
    # Google API
    google_calendar_credentials_path: Optional[str] = None
    gmail_credentials_path: Optional[str] = None
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Voice Configuration
    stt_model: str = "base"
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # MCP Servers
    mcp_memory_db_url: str = "http://localhost:8001"
    mcp_vector_db_url: str = "http://localhost:8002"
    mcp_telegram_url: str = "http://localhost:8003"
    mcp_calendar_url: str = "http://localhost:8004"
    mcp_gmail_url: str = "http://localhost:8005"
    mcp_windows_os_url: str = "http://localhost:8006"
    mcp_voice_url: str = "http://localhost:8007"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
