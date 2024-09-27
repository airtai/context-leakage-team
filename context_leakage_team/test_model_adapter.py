import json
from pathlib import Path

import requests
from pydantic import BaseModel

CONFIG_PATH = Path(__file__).parent / ".." / "tested_model_api_config.json"


class Config(BaseModel):
    url: str
    token: str


def load_config(config_path: Path) -> Config:
    with config_path.open() as file:
        config_data = json.load(file)
    return Config(**config_data)


config = load_config(CONFIG_PATH)


def send_msg_to_model(msg: str, config: Config = config) -> str:
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
    url = config.url
    token = config.token

    if not url or not token:
        raise ValueError("URL and token must be provided in the config file.")

    headers = {"Authorization": f"Bearer {token}", "Content-type": "application/json"}

    data = {"messages": [{"role": "user", "content": msg}]}

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    return response.json().get("content", "")  # type: ignore
