from pathlib import Path
from typing import Any

from autogen.agentchat import ConversableAgent


class PromptLeakageClassifierAgent(ConversableAgent):  # type: ignore[misc]
    SYSTEM_MESSAGE = (Path(__file__).parent / "system_message.md").read_text()

    def __init__(
        self,
        confidential_part: str,
        non_confidential_part: str,
        **kwargs: Any,
    ):
        """Initialize PromptLeakageClassifierAgent."""
        super().__init__(
            name="Prompt_Leakage_Classifier",
            description="Detect and classify prompt leakage in the model's response.",
            system_message=self.SYSTEM_MESSAGE.format(
                confidential_part=confidential_part,
                not_confidential_part=non_confidential_part,
            ),
            **kwargs,
        )
