from typing import Annotated, Callable, Optional

import requests


def create_send_msg_to_model(
    _url: str,
    _token: Optional[str] = None,
) -> Callable[[str], str]:
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
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        url = _url
        token = _token

        headers = {
            "Content-type": "application/json",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        data = {"messages": [{"role": "user", "content": msg}]}

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Ensure we raise an error for bad responses
        model_response = response.json().get("content")
        if not model_response:
            raise ValueError("No 'content' field found in API response")

        return model_response  # type: ignore

    return send_msg_to_model
