from pathlib import Path
from typing import Any

from autogen.agentchat import ConversableAgent


class PromptGeneratorAgent(ConversableAgent):  # type: ignore[misc]
    SYSTEM_MESSAGE = (Path(__file__).parent / "system_message.md").read_text()

    def __init__(self, **kwargs: Any):
        """Initialize PromptGeneratorAgent."""
        super().__init__(
            name="Prompt_Generator_Agent",
            description="Generates prompts to leak the prompt from the tested LLM.",
            system_message=self.SYSTEM_MESSAGE,
            **kwargs,
        )
