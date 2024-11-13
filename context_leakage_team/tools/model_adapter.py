from os import environ
from typing import Annotated

import requests


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
    url = environ.get("TESTED_MODEL_URL", "")
    token = environ.get("TESTED_MODEL_TOKEN", "")

    if not url or not token:
        raise ValueError("URL and token must be in environment variables")

    headers = {"Authorization": f"Bearer {token}", "Content-type": "application/json"}

    data = {"messages": [{"role": "user", "content": msg}]}

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    model_response = response.json().get("content")
    if not model_response:
        raise ValueError("No 'content' field found in API response")

    return model_response  # type: ignore
