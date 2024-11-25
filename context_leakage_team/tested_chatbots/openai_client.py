from asyncio import Queue
from contextlib import AsyncContextDecorator
from functools import lru_cache
from os import environ

from openai import AsyncOpenAI
from pydantic import BaseModel


class OpenAIGPTConfig(BaseModel):
    api_key: str


class JSONConfig(BaseModel):
    list_of_GPTs: list[OpenAIGPTConfig]  # noqa: N815
    batch_size: int = 1


class OpenAIClientWrapper(AsyncContextDecorator):
    def __init__(self, queue: Queue[AsyncOpenAI]) -> None:
        """OpenAIClientWrapper."""
        self.client: AsyncOpenAI | None = None
        self.queue: Queue[AsyncOpenAI] = queue

    async def __aenter__(self):  # type: ignore
        """__aenter__ method."""
        self.client = await self.queue.get()
        return self.client

    async def __aexit__(self, *exc):  # type: ignore
        """__aexit__ method."""
        if self.client:
            await self.queue.put(self.client)


class GPTRobin:
    def __init__(
        self,
        GPTs_to_use: list[OpenAIGPTConfig],  # noqa: N803
        batch_size: int = 1,
    ) -> None:
        """GPTRobin."""
        self.batch_size = batch_size
        self.client_queue = Queue()  # type: ignore
        clients = [
            AsyncOpenAI(
                api_key=gpt.api_key,
            )
            for gpt in GPTs_to_use
        ]
        for _ in range(batch_size):
            for c in clients:
                self.client_queue.put_nowait(c)

    def get_client(self) -> OpenAIClientWrapper:
        return OpenAIClientWrapper(self.client_queue)


@lru_cache(maxsize=1)
def get_gpt_robin():  # type: ignore
    robin = GPTRobin(
        GPTs_to_use=[
            OpenAIGPTConfig(api_key=environ["OPENAI_API_KEY"]),
        ],
        batch_size=1,
    )
    return robin
