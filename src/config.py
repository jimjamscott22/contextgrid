"""
Configuration management for ContextGrid CLI and direct database access.
Handles environment variables and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv
import sys

# Add src to python path to allow importing src.utils
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
from src.utils.paths import get_base_dir

# Load environment variables from .env file if it exists
BASE_DIR = get_base_dir()
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
    API_URL: str = os.getenv("API_URL", "http://localhost:8003")
    
    # Legacy API_ENDPOINT for backward compatibility
    if not API_URL and os.getenv("API_ENDPOINT"):
        API_URL = os.getenv("API_ENDPOINT", "http://localhost:8003")
    
    # =========================
    # Database Configuration
    # =========================
    
    # MySQL/MariaDB Configuration
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
        if not cls.MYSQL_USER:
            return False, "MySQL/MariaDB backend requires MYSQL_USER environment variable"
        if not cls.MYSQL_PASSWORD:
            return False, "MySQL/MariaDB backend requires MYSQL_PASSWORD environment variable"
        
        return True, ""
    
    @classmethod
    def get_mode_description(cls) -> str:
        """Get a human-readable description of the current configuration mode."""
        if cls.USE_API:
            return f"API mode (connecting to {cls.API_URL})"
        else:
            return f"Direct MySQL/MariaDB mode ({cls.MYSQL_USER}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE})"


# Global config instance
config = Config()
