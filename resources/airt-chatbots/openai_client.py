import json

from contextlib import AsyncContextDecorator
from asyncio import Queue
from functools import lru_cache
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from config import get_config


class AzureGPTConfig(BaseModel):
    api_key: str
    deployment_name: str
    azure_endpoint: str


class JSONConfig(BaseModel):
    list_of_GPTs: list[AzureGPTConfig]
    api_version: str = "2024-06-01"
    batch_size: int = 1


class AzureClientWrapper(AsyncContextDecorator):
    def __init__(self, queue) -> None:
        self.azure_client = None
        self.queue: Queue = queue
    
    async def __aenter__(self):
        self.azure_client = await self.queue.get()
        return self.azure_client
    
    async def __aexit__(self, *exc):
        await self.queue.put(self.azure_client)
        return True


class GPTRobin:
    def __init__(self, GPTs_to_use: list[AzureGPTConfig], api_version: str = "2024-06-01", batch_size: int = 1) -> None:
        self.batch_size = batch_size
        self.client_queue = Queue()
        clients = []
        for gpt in GPTs_to_use:
            clients.append(
                AsyncAzureOpenAI(
                    api_version=api_version,
                    api_key=gpt.api_key,
                    azure_deployment=gpt.deployment_name,
                    azure_endpoint=gpt.azure_endpoint
                )
            )
        print("Generating pool of", len(clients), "GPTs with each repeated in queue", batch_size, "times")
        for _ in range(batch_size):
            for c in clients:
                self.client_queue.put_nowait(c)
                

    def get_azure_client(self) -> AsyncAzureOpenAI:
        return AzureClientWrapper(self.client_queue)


config = get_config()


@lru_cache(maxsize=1)
def get_gpt_robin():
    with open(config.JSON_CONFIG_PATH, "r", encoding="utf-8") as f:
        gpt_config = json.load(f)
    robin_config = JSONConfig.model_validate(gpt_config)
    robin = GPTRobin(
        GPTs_to_use=robin_config.list_of_GPTs,
        api_version=robin_config.api_version,
        batch_size=robin_config.batch_size
    )
    return robin
