from fastapi import APIRouter, status
from pydantic import BaseModel

from .config import get_config
from .prompt_loader import get_level_config
from .service import process_messages

router = APIRouter()

config = get_config()

low = get_level_config(config.LOW_SYS_PROMPT_PATH)
medium = get_level_config(config.MEDIUM_SYS_PROMPT_PATH)
high = get_level_config(config.HIGH_SYS_PROMPT_PATH)


class Message(BaseModel):
    role: str = "user"
    content: str


class Messages(BaseModel):
    messages: list[Message]


@router.post("/low", status_code=status.HTTP_200_OK)
async def low_level(messages: Messages) -> dict[str, str]:
    resp = await process_messages(messages=messages.model_dump(), lvl_config=low)

    return resp


@router.post("/medium", status_code=status.HTTP_200_OK)
async def medium_level(messages: Messages) -> dict[str, str]:
    resp = await process_messages(messages=messages.model_dump(), lvl_config=medium)

    return resp


@router.post("/high", status_code=status.HTTP_200_OK)
async def high_level(messages: Messages) -> dict[str, str]:
    resp = await process_messages(messages=messages.model_dump(), lvl_config=high)

    return resp
