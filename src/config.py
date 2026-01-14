"""
Configuration management for ContextGrid CLI and direct database access.
Handles environment variables and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Config:
    """Configuration class for CLI and database connection."""
    
    # =========================
    # CLI Mode Configuration
    # =========================
    
    # USE_API determines whether CLI uses API or direct database access
    # - "true" or "1": Use API mode (CLI makes HTTP requests to API server)
    # - "false" or "0": Use direct mode (CLI accesses database directly)
    # Default: "true" (maintains current behavior of using API)
    USE_API: bool = os.getenv("USE_API", "true").lower() in ("true", "1", "yes")
    
    # API_URL is the base URL for the API server (used when USE_API=true)
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    
    # Legacy API_ENDPOINT for backward compatibility
    if not API_URL and os.getenv("API_ENDPOINT"):
        API_URL = os.getenv("API_ENDPOINT", "http://localhost:8000")
    
    # =========================
    # Database Configuration
    # =========================
    
    # DB_TYPE determines which database backend to use
    # Options: "sqlite" or "mysql"
    # Default: "sqlite"
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").lower()
    
    # SQLite Configuration
    DB_PATH: str = os.getenv("DB_PATH", "data/projects.db")
    
    # MySQL Configuration
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "contextgrid")
    
    @classmethod
    def validate(cls) -> Tuple[bool, str]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # If using MySQL, ensure credentials are provided
        if cls.DB_TYPE == "mysql":
            if not cls.MYSQL_USER:
                return False, "MySQL backend requires MYSQL_USER environment variable"
            if not cls.MYSQL_PASSWORD:
                return False, "MySQL backend requires MYSQL_PASSWORD environment variable"
        
        # Validate DB_TYPE
        if cls.DB_TYPE not in ("sqlite", "mysql"):
            return False, f"Invalid DB_TYPE: {cls.DB_TYPE}. Must be 'sqlite' or 'mysql'"
        
        return True, ""
    
    @classmethod
    def get_mode_description(cls) -> str:
        """Get a human-readable description of the current configuration mode."""
        if cls.USE_API:
            return f"API mode (connecting to {cls.API_URL})"
        else:
            if cls.DB_TYPE == "mysql":
                return f"Direct MySQL mode ({cls.MYSQL_USER}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE})"
            else:
                return f"Direct SQLite mode ({cls.DB_PATH})"


# Global config instance
config = Config()
