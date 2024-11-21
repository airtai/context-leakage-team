import functools
from collections.abc import Iterable
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import Any, Callable

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
from context_leakage_team.workflow.scenarios.scenario_template import ScenarioTemplate

from ...llm_config import llm_config


@dataclass
class FunctionToRegister:
    function: Callable[..., Any]
    name: str
    description: str


class ContextLeakageScenario(ScenarioTemplate):
    DEFAULT_LOG_PATH = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / ".."
        / "reports"
        / "default_report.csv"
    )
    TESTED_MODEL_CONFIDENTIAL_PATH = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / ".."
        / "tested_model_config"
        / "tested_model_confidential.md"
    )
    TESTED_MODEL_NON_CONFIDENTIAL_PATH = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / ".."
        / "tested_model_config"
        / "tested_model_non_confidential.md"
    )

    def __init__(self, ui: UI, params: dict[str, Any]) -> None:
        """Initialize the scenario."""
        super().__init__(ui, params)
        self.context_leak_log_save_path = self.DEFAULT_LOG_PATH
        self.counter = 0

        self.model_level = self.ui.multiple_choice(
            sender="Context leakage team",
            prompt="What model would you like to test?",
            choices=["low", "medium", "high"],
        )

        self.max_round = int(
            self.ui.multiple_choice(
                sender="Context leakage team",
                prompt="How much rounds would you like to run?",
                choices=["1", "5", "20", "50", "100"],
            )
        )

    def setup_environment(self) -> None:
        pass

    def setup_agents(self) -> Iterable[Agent]:
        """Create agents specific to context leakage."""
        confidential_text = self.TESTED_MODEL_CONFIDENTIAL_PATH.read_text()
        non_confidential_text = self.TESTED_MODEL_NON_CONFIDENTIAL_PATH.read_text()

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

    def setup_group_chat(self, agents: Iterable[Agent]) -> GroupChatManager:
        """Initialize group chat with specific agents."""
        prompt_generator, context_leak_classifier, user_proxy = agents

        def custom_speaker_selection(
            last_speaker: Agent, groupchat: GroupChat
        ) -> Agent:
            messages = groupchat.messages
            if last_speaker is prompt_generator:
                return (
                    self._validate_tool_call(
                        messages, prompt_generator, "send a message to the model"
                    )
                    or user_proxy
                )

            if last_speaker is context_leak_classifier:
                return (
                    self._validate_tool_call(
                        messages,
                        context_leak_classifier,
                        "classify the context leakage",
                    )
                    or user_proxy
                )

            if last_speaker is user_proxy:
                prev_speaker = messages[-2]["name"]
                if prev_speaker == "Prompt_Generator_Agent":
                    return context_leak_classifier
                elif prev_speaker == "Context_Leak_Classifier_Agent":
                    return prompt_generator

            return prompt_generator

        group_chat = GroupChat(
            agents=[prompt_generator, context_leak_classifier, user_proxy],
            messages=[],
            max_round=100,
            speaker_selection_method=custom_speaker_selection,
        )

        return GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    def execute_scenario(self, group_chat_manager: GroupChatManager) -> str:
        """Run the main scenario logic."""
        initial_message = self.params.get("initial_message", "Start the test.")

        function_to_register = self.get_function_to_register(
            model_level=self.model_level
        )

        self.counter = 0

        register_function(
            function_to_register.function,
            caller=group_chat_manager.groupchat.agents[0],
            executor=group_chat_manager.groupchat.agents[2],
            name=function_to_register.name,
            description=function_to_register.description,
        )

        log_context_leakage = create_log_context_leakage_function(
            save_path=self.context_leak_log_save_path, model_name=self.model_level
        )

        @functools.wraps(log_context_leakage)
        def function_call_counter(*args: Any, **kwargs: dict[str, Any]) -> Any:
            retval = log_context_leakage(*args, **kwargs)
            if retval == "OK":
                self.counter += 1
            return retval

        register_function(
            function_call_counter,
            caller=group_chat_manager.groupchat.agents[1],
            executor=group_chat_manager.groupchat.agents[2],
            name="log_context_leakage",
            description="Save context leak attempt",
        )

        chat_result = group_chat_manager.groupchat.agents[1].initiate_chat(
            group_chat_manager,
            message=initial_message,
            summary_method="reflection_with_llm",
        )
        return chat_result.summary  # type: ignore [no-any-return]

    def generate_report(self) -> str:
        """Generate markdown report."""
        return generate_markdown_report(
            name=type(self).__name__, log_path=self.context_leak_log_save_path
        )

    def _validate_tool_call(
        self, messages: list[dict[str, Any]], agent: Agent, action: str
    ) -> Agent | None:
        """Validate if the tool call is made."""
        if "tool_calls" not in messages[-1] and len(messages) > 1:
            self.ui.text_message(
                sender="Context leakage team",
                recipient=agent.name,
                body=f"Please call the function to {action}.",
            )
            return agent
        return None

    def get_function_to_register(self, model_level: str) -> FunctionToRegister:
        """Return the function to register for model interaction."""
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
