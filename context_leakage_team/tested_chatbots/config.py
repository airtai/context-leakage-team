from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class ChatbotConfiguration(BaseSettings):
    LOW_SYS_PROMPT_PATH: Path = Path(__file__).parent / "prompts/low.json"
    MEDIUM_SYS_PROMPT_PATH: Path = Path(__file__).parent / "prompts/medium.json"
    HIGH_SYS_PROMPT_PATH: Path = Path(__file__).parent / "prompts/high.json"

    INPUT_LIMIT: Optional[int] = None

    MAX_RETRIES: int = 5
    INITIAL_SLEEP_TIME_S: int = 5


@lru_cache(maxsize=1)
def get_config() -> ChatbotConfiguration:
    return ChatbotConfiguration()
