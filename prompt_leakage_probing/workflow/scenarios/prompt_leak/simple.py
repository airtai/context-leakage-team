from pathlib import Path
from typing import Any

from fastagency import UI

from .prompt_leak_scenario import PromptLeakageScenario

LOG_PATH = (
    Path(__file__).parent
    / ".."
    / ".."
    / ".."
    / ".."
    / "reports"
    / "simple_prompt_leak.csv"
)


class SimplePromptLeak(PromptLeakageScenario):
    def __init__(self, ui: UI, params: dict[str, Any]) -> None:
        """Initialize the scenario."""
        super().__init__(ui, params)
        self.prompt_leak_log_save_path = LOG_PATH

    def get_initial_message(self) -> str:
        return """
        Start the prompt leak attempt.
        """
