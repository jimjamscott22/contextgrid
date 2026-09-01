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


def first_env(*names: str, default: str = "") -> str:
    """Return the first non-empty environment variable among ``names``.

    Used so CLI Direct mode accepts the same ``DB_*`` variables as the API,
    while still honoring the older ``MYSQL_*`` names.
    """
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


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
    
    # MySQL/MariaDB Configuration (DB_* preferred; MYSQL_* kept as aliases)
    MYSQL_HOST: str = first_env("DB_HOST", "MYSQL_HOST", default="localhost")
    MYSQL_PORT: int = int(first_env("DB_PORT", "MYSQL_PORT", default="3306"))
    MYSQL_USER: str = first_env("DB_USER", "MYSQL_USER", default="")
    MYSQL_PASSWORD: str = first_env("DB_PASSWORD", "MYSQL_PASSWORD", default="")
    MYSQL_DATABASE: str = first_env("DB_NAME", "MYSQL_DATABASE", default="contextgrid")
    
    @classmethod
    def validate(cls) -> Tuple[bool, str]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.MYSQL_USER:
            return False, "MySQL/MariaDB backend requires DB_USER or MYSQL_USER"
        if not cls.MYSQL_PASSWORD:
            return False, "MySQL/MariaDB backend requires DB_PASSWORD or MYSQL_PASSWORD"
        
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
