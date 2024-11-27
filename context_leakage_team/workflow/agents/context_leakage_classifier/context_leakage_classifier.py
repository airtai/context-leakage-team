from pathlib import Path
from typing import Any

from autogen.agentchat import ConversableAgent


class ContextLeakageClassifierAgent(ConversableAgent):  # type: ignore[misc]
    SYSTEM_MESSAGE = (Path(__file__).parent / "system_message.md").read_text()

    def __init__(
        self,
        confidential_part: str,
        non_confidential_part: str,
        **kwargs: Any,
    ):
        """Initialize ContextLeakageClassifierAgent."""
        super().__init__(
            name="Context_Leakage_Classifier",
            description="Detect and classify context leakage in the model's response.",
            system_message=self.SYSTEM_MESSAGE.format(
                confidential_part=confidential_part,
                not_confidential_part=non_confidential_part,
            ),
            **kwargs,
        )
