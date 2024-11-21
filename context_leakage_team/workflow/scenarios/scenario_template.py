from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from autogen import GroupChatManager
from autogen.agentchat import Agent
from fastagency import UI


class ScenarioTemplate(ABC):
    def __init__(self, ui: UI, params: dict[str, Any]) -> None:
        """Initialize the scenario."""
        self.ui = ui
        self.params = params

    def run(self) -> str:
        """Template method for running the scenario."""
        self.setup_environment()
        agents = self.setup_agents()
        group_chat_manager = self.setup_group_chat(agents)
        return self.execute_scenario(group_chat_manager)

    def report(self) -> None:
        """Generate a report for the scenario."""
        self.ui.text_message(
            sender="Context leakage team",
            recipient="User",
            body=self.generate_report(),
        )

    @abstractmethod
    def setup_environment(self) -> None:
        """Set up any necessary environment variables or paths."""
        pass

    @abstractmethod
    def setup_agents(self) -> Iterable[Agent]:
        """Create and configure agents."""
        pass

    @abstractmethod
    def setup_group_chat(self, agents: Iterable[Agent]) -> GroupChatManager:
        """Set up the group chat and its manager."""
        pass

    @abstractmethod
    def execute_scenario(self, group_chat_manager: GroupChatManager) -> str:
        """Execute the specific scenario logic."""
        pass

    @abstractmethod
    def generate_report(self) -> str:
        """Generate a markdown report for the scenario."""
        pass
