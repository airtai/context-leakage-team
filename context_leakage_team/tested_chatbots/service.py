import asyncio
import json
import traceback
from typing import Any

import openai
from fastapi import HTTPException, status

from .config import get_config
from .openai_client import get_gpt_robin
from .prompt_loader import LevelConfig, functions, generate_random_addresses

config = get_config()

gpt_robin = get_gpt_robin()


async def process_messages(  # noqa: C901
    messages: dict[str, Any], lvl_config: LevelConfig
) -> dict[str, Any]:
    chat_messages: list = messages.get("messages")  # type: ignore
    if chat_messages is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing root field messages",
        )

    if (
        config.INPUT_LIMIT is not None
        and len(chat_messages[-1]["content"]) > config.INPUT_LIMIT
    ):
        raise HTTPException(
            status_code=452, detail="Content size exceeds specified limit"
        )

    chat_messages.insert(0, {"role": "system", "content": lvl_config.system_prompt})

    sleep_time = config.INITIAL_SLEEP_TIME_S
    attempt = 0

    async with gpt_robin.get_client() as client:
        while attempt < config.MAX_RETRIES:
            attempt += 1
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=chat_messages,
                    functions=functions,
                    function_call="auto",
                )

                if response.choices[0].finish_reason == "function_call":
                    chat_messages.append(response.choices[0].message)
                    tool_call = response.choices[0].message.function_call
                    fun_args = json.loads(tool_call.arguments)
                    res = generate_random_addresses(**fun_args)

                    chat_messages.append(
                        {
                            "role": "function",
                            "content": json.dumps(res),
                            "name": "get_store_locations",
                        }
                    )
                    response = await client.chat.completions.create(
                        model="gpt-4o",
                        messages=chat_messages,
                        functions=functions,
                        function_call=None,  # Disabling calling function again
                    )

                for w in lvl_config.canary_words:
                    if w in response.choices[0].message.content:
                        return {
                            "role": "assistant",
                            "content": "I cannot assist with this request.",
                        }

                if lvl_config.use_guardrails:
                    guard_messages = [
                        {"role": "system", "content": lvl_config.guardrail_prompt},
                        {
                            "role": "user",
                            "content": response.choices[0].message.content,
                        },
                    ]

                    guard_response = await client.chat.completions.create(
                        model="gpt-4o", messages=guard_messages
                    )

                    if guard_response.choices[0].message.content == "GOOD":
                        return {
                            "role": "assistant",
                            "content": response.choices[0].message.content,
                        }
                    return {
                        "role": "assistant",
                        "content": "I cannot assist with this request.",
                    }
                return {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                }

            except openai.RateLimitError:
                await asyncio.sleep(sleep_time)
                sleep_time *= 2
            except Exception as e:
                traceback.print_exc(e)  # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected exception happened {e}",
                ) from e
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="You reached OpenAI rate limit",
    )
