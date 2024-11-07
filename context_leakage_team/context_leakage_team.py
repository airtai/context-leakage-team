import os
from pathlib import Path
from typing import Any

from autogen import GroupChat, GroupChatManager, register_function
from autogen.agentchat import ConversableAgent, UserProxyAgent
from autogen.agentchat.agent import Agent
from fastagency import UI, FastAgency
from fastagency.runtimes.autogen import AutoGenWorkflows
from fastagency.ui.mesop import MesopUI
from model_adapter import send_msg_to_model
from model_configs import (
    get_context_leakage_black_box_prompt,
    get_context_leakage_classifier_prompt,
)

tested_model_confidential = (
    Path(__file__).parent
    / ".."
    / "tested_model_config"
    / "tested_model_confidential.md"
)
tested_model_non_confidential = (
    Path(__file__).parent
    / ".."
    / "tested_model_config"
    / "tested_model_non_confidential.md"
)

llm_config = {
    "config_list": [
        {
            "model": os.getenv("AZURE_GPT4o_MODEL"),  # noqa
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "base_url": os.getenv("AZURE_API_ENDPOINT"),
            "api_type": "azure",
            "api_version": "2024-02-15-preview",
        }
    ],
    "temperature": 0.8,
}

wf = AutoGenWorkflows()


@wf.register(
    name="context leak attempt", description="Attempt to leak context from tested LLM."
)  # type: ignore
def context_leaking(ui: UI, params: dict[str, Any]) -> str:
    def is_termination_msg(msg: dict[str, Any]) -> bool:
        return msg["content"] is not None and "TERMINATE" in msg["content"]

    initial_message = ui.text_input(
        sender="Workflow",
        recipient="User",
        prompt="I can help you test context leakage",
    )

    prompt_generator = ConversableAgent(
        name="Prompt_Generator_Agent",
        system_message=get_context_leakage_black_box_prompt(),
        llm_config=llm_config,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        description="Generates prompts to leak context from the tested LLM.",
    )

    context_leak_classifier = ConversableAgent(
        name="Context_Leak_Classifier_Agent",
        system_message=get_context_leakage_classifier_prompt(
            confidential_part=tested_model_confidential.read_text(),
            not_confidential_part=tested_model_non_confidential.read_text(),
            tools="",
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        description="Detects context leakage in the response from the tested LLM.",
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy_Agent",
        human_input_mode="NEVER",
    )

    register_function(
        send_msg_to_model,
        caller=prompt_generator,
        executor=user_proxy,
        name="send_msg_to_model",
        description="Sends a message to the tested LLM",
    )

    def state_transition(last_speaker: Agent, groupchat: GroupChat) -> Agent:
        if last_speaker is prompt_generator:
            # init -> retrieve
            return user_proxy
        elif last_speaker is user_proxy:
            # retrieve: action 1 -> action 2
            return context_leak_classifier
        elif last_speaker is context_leak_classifier:
            # action 2 -> action 1
            return prompt_generator

        return prompt_generator

    group_chat = GroupChat(
        agents=[prompt_generator, context_leak_classifier, user_proxy],
        messages=[],
        max_round=20,
        speaker_selection_method=state_transition,
    )
    group_chat_manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    chat_result = context_leak_classifier.initiate_chat(
        group_chat_manager,
        message=initial_message,
        summary_method="reflection_with_llm",
    )

    return chat_result.summary  # type: ignore[no-any-return]


app = FastAgency(provider=wf, ui=MesopUI(), title="Context leak chat")
