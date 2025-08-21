import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from pathlib import Path


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


@dataclass
class LLMConfig:
    openai_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    together_model: str = "meta-llama/Llama-3-8b-chat-hf"
    max_retries: int = 3
    timeout: int = 30
    environment: str = "development"


def get_config(env: Optional[str] = None) -> LLMConfig:
    """Get configuration based on environment."""
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass
    
    if env is None:
        env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
    
    config = LLMConfig()
    config.environment = env
    
    # Load API keys and models based on environment
    if env == Environment.PRODUCTION.value:
        config.openai_api_key = os.getenv("OPENAI_API_KEY_PROD")
        config.together_api_key = os.getenv("TOGETHER_API_KEY_PROD")
        config.openai_model = os.getenv("OPENAI_MODEL_PROD", "gpt-4")
        config.together_model = os.getenv("TOGETHER_MODEL_PROD", "meta-llama/Llama-3-70b-chat-hf")
    else:
        config.openai_api_key = os.getenv("OPENAI_API_KEY_DEV")
        config.together_api_key = os.getenv("TOGETHER_API_KEY_DEV")
        config.openai_model = os.getenv("OPENAI_MODEL_DEV", "gpt-4o-mini")
        config.together_model = os.getenv("TOGETHER_MODEL_DEV", "meta-llama/Llama-3-8b-chat-hf")
    
    # Load shared settings
    config.max_retries = int(os.getenv("MAX_RETRIES", str(config.max_retries)))
    config.timeout = int(os.getenv("TIMEOUT", str(config.timeout)))
    
    return config