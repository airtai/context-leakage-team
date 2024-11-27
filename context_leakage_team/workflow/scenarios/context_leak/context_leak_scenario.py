import functools
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from autogen import GroupChat, GroupChatManager, register_function
from autogen.agentchat import Agent, ConversableAgent, UserProxyAgent
from fastagency import UI

from context_leakage_team.workflow.agents import (
    ContextLeakageClassifierAgent,
    ContextLeakagePromptGeneratorAgent,
)

from ...llm_config import llm_config
from ...tools.log_context_leakage import (
    create_log_context_leakage_function,
    generate_markdown_report,
)
from ...tools.model_adapter import create_send_msg_to_model
from ..scenario_template import ScenarioTemplate


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
        Path(__file__).parents[3] / "tested_chatbots" / "prompts" / "confidential.md"
    )
    TESTED_MODEL_NON_CONFIDENTIAL_PATH = (
        Path(__file__).parents[3]
        / "tested_chatbots"
        / "prompts"
        / "non_confidential.md"
    )

    def __init__(self, ui: UI, params: dict[str, Any]) -> None:
        """Initialize the scenario."""
        super().__init__(ui, params)
        self.context_leak_log_save_path = self.DEFAULT_LOG_PATH
        self.counter = 0
        self.model_level = "low"
        self.max_round = 1

    def setup_environment(self) -> None:
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

    def setup_context_leak_classifier_agent(self, executor: Agent) -> ConversableAgent:
        confidential_part = self.TESTED_MODEL_CONFIDENTIAL_PATH.read_text()
        non_confidential_part = self.TESTED_MODEL_NON_CONFIDENTIAL_PATH.read_text()

        context_leak_classifier = ContextLeakageClassifierAgent(
            confidential_part=confidential_part,
            non_confidential_part=non_confidential_part,
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda _: self.counter >= self.max_round,
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
            caller=context_leak_classifier,
            executor=executor,
            name="log_context_leakage",
            description="Save context leak attempt",
        )

        return context_leak_classifier

    def setup_prompt_generator_agent(self, executor: Agent) -> ConversableAgent:
        prompt_generator = ContextLeakagePromptGeneratorAgent(
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda _: self.counter >= self.max_round,
        )

        function_to_register = self.get_function_to_register(
            model_level=self.model_level
        )

        register_function(
            function_to_register.function,
            caller=prompt_generator,
            executor=executor,
            name=function_to_register.name,
            description=function_to_register.description,
        )

        return prompt_generator

    def setup_agents(self) -> Iterable[Agent]:
        """Create agents specific to context leakage."""
        user_proxy = UserProxyAgent(
            name="User_Proxy_Agent",
            human_input_mode="NEVER",
        )

        prompt_generator = self.setup_prompt_generator_agent(user_proxy)

        context_leak_classifier = self.setup_context_leak_classifier_agent(user_proxy)

        return [prompt_generator, context_leak_classifier, user_proxy]

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
        url = "http://localhost:8008"

        return FunctionToRegister(
            function=create_send_msg_to_model(_url=f"{url}/{model_level}"),
            name="send_msg_to_model",
            description="Sends a message to the tested LLM",
        )

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

    def get_initial_message(self) -> str:
        """Return the initial message for the scenario."""
        return "Start the context leak attempt."

    def execute_scenario(self, group_chat_manager: GroupChatManager) -> str:
        """Run the main scenario logic."""
        initial_message = self.get_initial_message()

        self.counter = 0

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
