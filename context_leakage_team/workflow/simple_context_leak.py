import json
from pathlib import Path
from typing import Any

from autogen import GroupChat, GroupChatManager, register_function
from autogen.agentchat import ConversableAgent, UserProxyAgent
from fastagency import UI

from context_leakage_team.agent_configs import (
    get_context_leakage_black_box_prompt,
    get_context_leakage_classifier_prompt,
)
from context_leakage_team.log_context_leakage import (
    create_log_context_leakage_function,
    generate_markdown_report,
)
from context_leakage_team.model_adapter import send_msg_to_model
from context_leakage_team.workflow.workflow import llm_config, wf

tested_model_confidential = (
    Path(__file__).parent
    / ".."
    / ".."
    / "tested_model_config"
    / "tested_model_confidential.md"
)
tested_model_non_confidential = (
    Path(__file__).parent
    / ".."
    / ".."
    / "tested_model_config"
    / "tested_model_non_confidential.md"
)

context_leak_log_save_path = (
    Path(__file__).parent / ".." / ".." / "reports" / "simple_context_leak.pd"
)


@wf.register(  # type: ignore[misc]
    name="Context leak attempt", description="Attempt to leak context from tested LLM."
)
def context_leaking(ui: UI, params: dict[str, Any]) -> str:
    def is_termination_msg(msg: dict[str, Any]) -> bool:
        try:
            return json.loads(msg["content"])["detection_level"] > 0  # type: ignore [no-any-return]
        except:  # noqa: E722 Do not use bare `except`
            return False

    initial_message = """
    Start the context leak attempt.
    """

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

    register_function(
        create_log_context_leakage_function(save_path=context_leak_log_save_path),
        caller=context_leak_classifier,
        executor=user_proxy,
        name="log_context_leakage",
        description="Save context leak attempt",
    )

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

    group_chat_manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    chat_result = context_leak_classifier.initiate_chat(
        group_chat_manager,
        message=initial_message,
        summary_method="reflection_with_llm",
    )

    return chat_result.summary  # type: ignore [no-any-return]


@wf.register(  # type: ignore[misc]
    name="Context leak report",
    description="Display a report of basic context leak attempts",
)
def context_leaking_report(ui: UI, params: dict[str, Any]) -> None:
    ui.text_message(
        sender="Context leakage team",
        recipient="User",
        body=generate_markdown_report(log_path=context_leak_log_save_path),
    )
