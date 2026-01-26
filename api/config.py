"""
Configuration management for ContextGrid API server.
Handles environment variables and provides sensible defaults.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Config:
    """Configuration class for API server and database connection."""
    
    # API Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "contextgrid")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Connection Pool Configuration
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Construct database connection URL.
        
        Returns:
            Database URL in format: mysql+pymysql://user:password@host:port/database
        """
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.DB_PASSWORD:
            return False, "DB_PASSWORD is required but not set"
        
        if not cls.DB_USER:
            return False, "DB_USER is required but not set"
        
        return True, None


# Global config instance
config = Config()
