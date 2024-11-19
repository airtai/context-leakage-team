import functools
from abc import ABC, abstractmethod
from collections import namedtuple
from os import environ
from pathlib import Path
from typing import Any

import autogen
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
from context_leakage_team.tools.model_adapter import create_send_msg_to_model

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


class Scenario(ABC):
    def __init__(self) -> None:
        """Initialize the scenario."""
        self.context_leak_log_save_path = DEFAULT_LOG_PATH
        self.counter = 0
        self.max_round = 20

    @abstractmethod
    def get_initial_message(self) -> str:
        pass

    def setup_group_chat(
        self,
        ui: UI,
        prompt_generator: Agent,
        context_leak_classifier: Agent,
        user_proxy: Agent,
        llm_config: dict[str, Any],
    ) -> GroupChatManager:
        def custom_speaker_selection_func(
            last_speaker: Agent, groupchat: autogen.GroupChat
        ) -> Agent:
            messages = groupchat.messages

            if last_speaker is prompt_generator:
                # Prompt generator must call the function to send a message to the model
                if "tool_calls" not in messages[-1] and len(messages) > 1:
                    ui.system_message(
                        sender="Context leakage team",
                        message="Please call the function to send a message to the model.",
                    )
                    return prompt_generator
                else:
                    return user_proxy

            if last_speaker is context_leak_classifier:
                if "tool_calls" not in messages[-1] and len(messages) > 1:
                    ui.system_message(
                        sender="Context leakage team",
                        message="Please call the function to classify the context leakage.",
                    )
                    return context_leak_classifier
                else:
                    return user_proxy

            if last_speaker is user_proxy:
                if messages[-2]["name"] == "Prompt_Generator_Agent":
                    return context_leak_classifier
                elif messages[-2]["name"] == "Context_Leak_Classifier_Agent":
                    return prompt_generator

            return prompt_generator

        group_chat = GroupChat(
            agents=[prompt_generator, context_leak_classifier, user_proxy],
            messages=[],
            max_round=100,
            speaker_selection_method=custom_speaker_selection_func,
        )

        return GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    def create_agents(
        self,
        llm_config: dict[str, Any],
        confidential_text: str,
        non_confidential_text: str,
    ) -> tuple[Agent, Agent, Agent]:
        prompt_generator = ConversableAgent(
            name="Prompt_Generator_Agent",
            system_message=get_context_leakage_black_box_prompt(),
            llm_config=llm_config,
            human_input_mode="NEVER",
            description="Generates prompts to leak context from the tested LLM.",
            code_execution_config=False,
            is_termination_msg=lambda x: self.counter >= self.max_round,
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

    def get_function_to_register(self, model_level: str) -> FunctionToRegister:
        url = environ.get("TESTED_MODEL_URL")
        token = environ.get("TESTED_MODEL_TOKEN")

        if not url or not token:
            raise ValueError(
                "MODEL_URL and MODEL_TOKEN environment variables must be set"
            )

        return FunctionToRegister(
            function=create_send_msg_to_model(
                _url=f"{url}/{model_level}", _token=token
            ),
            name="send_msg_to_model",
            description="Sends a message to the tested LLM",
        )

    def get_max_round(self, ui: UI) -> int:
        return int(
            ui.multiple_choice(
                sender="Context leakage team",
                prompt="How many rounds would you like to run?",
                choices=["5", "10", "20", "100"],
            )
        )

    def run(self, ui: UI, params: dict[str, Any]) -> str:
        """Run the scenario with provided UI and parameters."""
        initial_message = self.get_initial_message()

        model_level = ui.multiple_choice(
            sender="Context leakage team",
            prompt="What model would you like to test?",
            choices=["low", "medium", "high"],
        )

        function_to_register = self.get_function_to_register(model_level=model_level)
        self.counter = 0

        # Shared configuration and agent setup
        confidential_text = tested_model_confidential.read_text()
        non_confidential_text = tested_model_non_confidential.read_text()

        # Create agents
        prompt_generator, context_leak_classifier, user_proxy = self.create_agents(
            llm_config, confidential_text, non_confidential_text
        )

        self.max_round = self.get_max_round(ui)

        @functools.wraps(function_to_register.function)
        def function_call_counter(*args: Any, **kwargs: dict[str, Any]) -> Any:
            self.counter += 1
            return function_to_register.function(*args, **kwargs)

        # Register function based on the scenario
        register_function(
            function_call_counter,
            caller=prompt_generator,
            executor=user_proxy,
            name=function_to_register.name,
            description=function_to_register.description,
        )

        # Register the logging function
        register_function(
            create_log_context_leakage_function(
                save_path=self.context_leak_log_save_path,
                model_name=model_level,
            ),
            caller=context_leak_classifier,
            executor=user_proxy,
            name="log_context_leakage",
            description="Save context leak attempt",
        )

        # Set up and initiate group chat
        group_chat_manager = self.setup_group_chat(
            ui, prompt_generator, context_leak_classifier, user_proxy, llm_config
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
