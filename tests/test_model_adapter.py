from unittest.mock import patch

import pytest
import requests

from context_leakage_team.model_adapter import Config

# Import the send_msg_to_model function from your module
# from model_interface import send_msg_to_model


# Fixture to mock config file loading
@pytest.fixture
def _mock_config(monkeypatch):
    # This simulates the config that would be loaded from config.json
    mock_config_data = Config(
        **{"url": "https://mock-api-url.com/generate", "token": "MOCK_API_KEY"}
    )

    def mock_load_config():
        return mock_config_data

    monkeypatch.setattr(
        "context_leakage_team.model_adapter.load_config", mock_load_config
    )


# Test case for a successful API call
@pytest.mark.usefixtures("_mock_config")
@patch("requests.post")
def test_send_msg_success(mock_post):
    mock_response = {"content": "This is a mock response from the model."}
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    # Test the function
    from context_leakage_team.model_adapter import (
        send_msg_to_model,  # Import inside test for mock effect
    )

    response = send_msg_to_model("Test message")

    assert response == "This is a mock response from the model."


# Test case for API response missing 'response' field
@pytest.mark.usefixtures("_mock_config")
@patch("requests.post")
def test_send_msg_no_response_field(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {}

    # Test the function and expect an exception
    from context_leakage_team.model_adapter import send_msg_to_model

    with pytest.raises(Exception, match="No 'content' field found in API response"):
        send_msg_to_model("Test message")


# Test case for connection error handling
@pytest.mark.usefixtures("_mock_config")
@patch("requests.post")
def test_send_msg_connection_error(mock_post):
    # Simulate a connection error
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    # Test the function and expect an exception
    from context_leakage_team.model_adapter import send_msg_to_model

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        send_msg_to_model("Test message")
