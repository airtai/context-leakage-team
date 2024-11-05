import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings

ACC_API_KEY = os.environ.get("ACC_API_KEY", "")

class ChatbotConfiguration(BaseSettings):
    ACC_API_KEY: str
    JSON_CONFIG_PATH: str = "config.json"

    LOW_SYS_PROMPT_PATH: str = "prompts/low.json"
    MEDIUM_SYS_PROMPT_PATH: str = "prompts/medium.json"
    HIGH_SYS_PROMPT_PATH: str = "prompts/high.json"

    INPUT_LIMIT: Optional[int] = None

    MAX_RETRIES: int = 5
    INITIAL_SLEEP_TIME_S: int = 5


@lru_cache(maxsize=1)
def get_config():
    return ChatbotConfiguration(ACC_API_KEY=ACC_API_KEY)
