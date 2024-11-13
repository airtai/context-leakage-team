from unittest.mock import patch, MagicMock

import pytest
import requests


@pytest.fixture
def set_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TESTED_MODEL_URL", "http://test.com")
    monkeypatch.setenv("TESTED_MODEL_TOKEN", "test_token")

# Test case for a successful API call
@pytest.mark.usefixtures("set_env_vars")
@patch("requests.post")
def test_send_msg_success(mock_post: MagicMock) -> None:
    mock_response = {"content": "This is a mock response from the model."}
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    # Test the function
    from context_leakage_team.tools.model_adapter import (
        send_msg_to_model,  # Import inside test for mock effect
    )

    response = send_msg_to_model("Test message")

    assert response == "This is a mock response from the model."


# Test case for API response missing 'response' field
@pytest.mark.usefixtures("set_env_vars")
@patch("requests.post")
def test_send_msg_no_response_field(mock_post: MagicMock) -> None:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {}

    # Test the function and expect an exception
    from context_leakage_team.tools.model_adapter import send_msg_to_model

    with pytest.raises(Exception, match="No 'content' field found in API response"):
        send_msg_to_model("Test message")


# Test case for connection error handling
@pytest.mark.usefixtures("set_env_vars")
@patch("requests.post")
def test_send_msg_connection_error(mock_post: MagicMock) -> None:
    # Simulate a connection error
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    # Test the function and expect an exception
    from context_leakage_team.tools.model_adapter import send_msg_to_model

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        send_msg_to_model("Test message")
