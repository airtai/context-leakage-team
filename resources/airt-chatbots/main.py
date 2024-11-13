from typing import Annotated
from fastapi import status, FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from config import get_config
from service import process_messages
from prompt_loader import get_level_config

from pydantic import BaseModel

app = FastAPI(
    docs_url=None,
    servers=[
        {"url": "https://airt-chatbots-gecwdgakcse7g9bz.westeurope-01.azurewebsites.net/", "production": "Production environment"},
    ]
)

config = get_config()

low = get_level_config(config.LOW_SYS_PROMPT_PATH)
medium = get_level_config(config.MEDIUM_SYS_PROMPT_PATH)
high = get_level_config(config.HIGH_SYS_PROMPT_PATH)

class Message(BaseModel):
    role: str = "user"
    content: str

class Messages(BaseModel):
    messages: list[Message]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@app.post("/low", status_code=status.HTTP_200_OK)
async def low_level(messages: Messages, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    if token != config.ACC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    resp = await process_messages(messages=messages.model_dump(), lvl_config=low)

    return resp

@app.post("/medium", status_code=status.HTTP_200_OK)
async def medium_level(messages: Messages, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    if token != config.ACC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    resp = await process_messages(messages=messages.model_dump(), lvl_config=medium)

    return resp

@app.post("/high", status_code=status.HTTP_200_OK)
async def high_level(messages: Messages, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    if token != config.ACC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    resp = await process_messages(messages=messages.model_dump(), lvl_config=high)

    return resp
