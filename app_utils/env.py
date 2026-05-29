import os
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class EnvConfig:
    """
    Configuration for environment variables used across the QA Multi-Agent System.
    """
    # Google GenAI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # n8n Gateway (Legacy)
    N8N_GATEWAY_URL: str = os.getenv("N8N_GATEWAY_URL", "")

    # Third-party Integrations
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    JIRA_API_KEY: Optional[str] = os.getenv("JIRA_API_KEY")
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

    # Qdrant
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))

    def validate(self):
        if not self.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY must be set in the environment.")

# Singleton instance for global access
config = EnvConfig()
try:
    config.validate()
except Exception as e:
    import logging
    logging.warning(f"Config validation warning: {e}")
