import json
from pathlib import Path
from typing import Annotated

import requests
from pydantic import BaseModel


class Config(BaseModel):
    url: str
    token: str


CONFIG_PATH = (
    Path(__file__).parent
    / ".."
    / "tested_model_config"
    / "tested_model_api_config.json"
)

config_cache = None


def load_config(config_path: Path = CONFIG_PATH) -> Config:
    global config_cache
    if config_cache is None:
        with config_path.open() as file:
            config_data = json.load(file)
        config_cache = Config(**config_data)
    return config_cache


config = load_config(CONFIG_PATH)


def send_msg_to_model(
    msg: Annotated[str, "The message content to be sent to the model."],
) -> str:
    """Sends a message to a model endpoint specified in the configuration.

    Args:
        msg (str): The message content to be sent to the model.
        config (Config, optional): Configuration object containing 'url' and 'token'. Defaults to a global config.

    Returns:
        str: The response content from the model.

    Raises:
        ValueError: If the URL or token is not provided in the config.
        requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
    """
    config = load_config()
    url = config.url
    token = config.token

    if not url or not token:
        raise ValueError("URL and token must be provided in the config file.")

    headers = {"Authorization": f"Bearer {token}", "Content-type": "application/json"}

    data = {"messages": [{"role": "user", "content": msg}]}

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    model_response = response.json().get("content")
    if not model_response:
        raise ValueError("No 'content' field found in API response")

    return model_response  # type: ignore
