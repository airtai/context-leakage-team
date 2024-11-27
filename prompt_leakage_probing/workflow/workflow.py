from typing import Any

from fastagency import UI
from fastagency.runtimes.autogen import AutoGenWorkflows

from .scenarios import prompt_leak
from .scenarios.scenario_template import ScenarioTemplate

wf = AutoGenWorkflows()

prompt_leak_scenarios: dict[str, type[ScenarioTemplate]] = {
    name: getattr(prompt_leak, name) for name in prompt_leak.__all__
}


@wf.register(  # type: ignore[misc]
    name="Prompt leak attempt",
    description="Attempt to leak the prompt from tested LLM model.",
)
def prompt_leak_chat(ui: UI, params: dict[str, Any]) -> str:
    prompt_leak_scenario = ui.multiple_choice(
        sender="Prompt leakage team",
        prompt="Please select the type of prompt leakage attack you would like to attempt.",
        choices=list(prompt_leak_scenarios),
    )

    return prompt_leak_scenarios[prompt_leak_scenario](ui, params).run()


@wf.register(  # type: ignore[misc]
    name="Prompt leak attempt report",
    description="Report on the prompt leak attempt.",
)
def prompt_leak_report(ui: UI, params: dict[str, Any]) -> str:
    for scenario in prompt_leak_scenarios:
        prompt_leak_scenarios[scenario](ui, params).report()
    return (
        "You can find the reports for all prompt leak attempts in the messages above."
    )
