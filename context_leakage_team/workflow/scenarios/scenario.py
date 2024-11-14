from abc import ABC, abstractmethod
from collections import namedtuple
from pathlib import Path
from typing import Any

from autogen import GroupChat, GroupChatManager, register_function
from autogen.agentchat import Agent, ConversableAgent, UserProxyAgent
from fastagency import UI

from context_leakage_team.agent_configs import (
    get_context_leakage_black_box_prompt,
    get_context_leakage_classifier_prompt,
)
from context_leakage_team.tools.log_context_leakage import (
    create_log_context_leakage_function,
    generate_markdown_report,
)

from ..llm_config import llm_config

DEFAULT_LOG_PATH = (
    Path(__file__).parent / ".." / ".." / ".." / "reports" / "default_report.pd"
)

tested_model_confidential = (
    Path(__file__).parent
    / ".."
    / ".."
    / ".."
    / "tested_model_config"
    / "tested_model_confidential.md"
)

tested_model_non_confidential = (
    Path(__file__).parent
    / ".."
    / ".."
    / ".."
    / "tested_model_config"
    / "tested_model_non_confidential.md"
)

FunctionToRegister = namedtuple(
    "FunctionToRegister", ["function", "name", "description"]
)


def create_agents(
    llm_config: dict[str, Any], confidential_text: str, non_confidential_text: str
) -> tuple[Agent, Agent, Agent]:
    prompt_generator = ConversableAgent(
        name="Prompt_Generator_Agent",
        system_message=get_context_leakage_black_box_prompt(),
        llm_config=llm_config,
        human_input_mode="NEVER",
        description="Generates prompts to leak context from the tested LLM.",
        code_execution_config=False,
    )

    context_leak_classifier = ConversableAgent(
        name="Context_Leak_Classifier_Agent",
        system_message=get_context_leakage_classifier_prompt(
            confidential_part=confidential_text,
            not_confidential_part=non_confidential_text,
            tools="",
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
        description="Detects context leakage in the response from the tested LLM.",
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy_Agent",
        human_input_mode="NEVER",
    )

    return prompt_generator, context_leak_classifier, user_proxy


def setup_group_chat(
    prompt_generator: Agent,
    context_leak_classifier: Agent,
    user_proxy: Agent,
    llm_config: dict[str, Any],
) -> GroupChatManager:
    graph_dict = {
        user_proxy: [context_leak_classifier, prompt_generator],
        context_leak_classifier: [user_proxy],
        prompt_generator: [user_proxy],
    }

    group_chat = GroupChat(
        agents=[prompt_generator, context_leak_classifier, user_proxy],
        messages=[],
        max_round=20,
        allowed_or_disallowed_speaker_transitions=graph_dict,
        speaker_transitions_type="allowed",
    )

    return GroupChatManager(groupchat=group_chat, llm_config=llm_config)


class Scenario(ABC):
    def __init__(self) -> None:
        """Initialize the scenario."""
        self.context_leak_log_save_path = DEFAULT_LOG_PATH

    @abstractmethod
    def get_initial_message(self) -> str:
        pass

    @abstractmethod
    def get_function_to_register(self) -> FunctionToRegister:
        pass

    def run(self, ui: UI, params: dict[str, Any]) -> str:
        """Run the scenario with provided UI and parameters."""
        initial_message = self.get_initial_message()
        function_to_register = self.get_function_to_register()

        # Shared configuration and agent setup
        confidential_text = tested_model_confidential.read_text()
        non_confidential_text = tested_model_non_confidential.read_text()

        # Create agents
        prompt_generator, context_leak_classifier, user_proxy = create_agents(
            llm_config, confidential_text, non_confidential_text
        )

        # Register function based on the scenario
        register_function(
            function_to_register.function,
            caller=prompt_generator,
            executor=user_proxy,
            name=function_to_register.name,
            description=function_to_register.description,
        )

        # Register the logging function
        register_function(
            create_log_context_leakage_function(
                save_path=self.context_leak_log_save_path
            ),
            caller=context_leak_classifier,
            executor=user_proxy,
            name="log_context_leakage",
            description="Save context leak attempt",
        )

        # Set up and initiate group chat
        group_chat_manager = setup_group_chat(
            prompt_generator, context_leak_classifier, user_proxy, llm_config
        )

        chat_result = context_leak_classifier.initiate_chat(
            group_chat_manager,
            message=initial_message,
            summary_method="reflection_with_llm",
        )

        return chat_result.summary  # type: ignore [no-any-return]

    def report(self, ui: UI, params: dict[str, Any]) -> None:
        """Default report method; same for all subclasses."""
        ui.text_message(
            sender="Context leakage team",
            recipient="User",
            body=generate_markdown_report(log_path=self.context_leak_log_save_path),
        )
