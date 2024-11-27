from pathlib import Path
from typing import Any

from autogen.agentchat import ConversableAgent


class ContextLeakagePromptGeneratorAgent(ConversableAgent):  # type: ignore[misc]
    SYSTEM_MESSAGE = (Path(__file__).parent / "system_message.md").read_text()

    def __init__(self, **kwargs: Any):
        """Initialize ContextLeakagePromptGeneratorAgent."""
        super().__init__(
            name="Prompt_Generator_Agent",
            description="Generates prompts to leak context from the tested LLM.",
            system_message=self.SYSTEM_MESSAGE,
            **kwargs,
        )
