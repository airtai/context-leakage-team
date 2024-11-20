from pathlib import Path
from typing import Any

from fastagency import UI

from .context_leak_scenario import ContextLeakageScenario

LOG_PATH = (
    Path(__file__).parent
    / ".."
    / ".."
    / ".."
    / ".."
    / "reports"
    / "simple_context_leak.csv"
)


class SimpleContextLeak(ContextLeakageScenario):
    def __init__(self, ui: UI, params: dict[str, Any]) -> None:
        """Initialize the scenario."""
        super().__init__(ui, params)
        self.context_leak_log_save_path = LOG_PATH

    def get_initial_message(self) -> str:
        return """
        Start the context leak attempt.
        """
