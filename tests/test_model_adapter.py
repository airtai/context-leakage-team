from unittest.mock import patch, MagicMock

import pytest
import requests

from context_leakage_team.workflow.tools.model_adapter import create_send_msg_to_model


# Test case for a successful API call
@patch("requests.post")
def test_send_msg_success(mock_post: MagicMock) -> None:
    mock_response = {"content": "This is a mock response from the model."}
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response


    send_msg_to_model = create_send_msg_to_model("http://test.com", "test_token")

    response = send_msg_to_model("Test message")

    assert response == "This is a mock response from the model."


# Test case for API response missing 'response' field
@patch("requests.post")
def test_send_msg_no_response_field(mock_post: MagicMock) -> None:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {}

    send_msg_to_model = create_send_msg_to_model("http://test.com", "test_token")

    with pytest.raises(Exception, match="No 'content' field found in API response"):
        send_msg_to_model("Test message")


# Test case for connection error handling
@patch("requests.post")
def test_send_msg_connection_error(mock_post: MagicMock) -> None:
    # Simulate a connection error
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    send_msg_to_model = create_send_msg_to_model("http://test.com", "test_token")

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        send_msg_to_model("Test message")
