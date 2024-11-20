from typing import Any

from fastagency import UI
from fastagency.runtimes.autogen import AutoGenWorkflows

from . import scenarios
from .scenarios.scenario import Scenario

wf = AutoGenWorkflows()

context_leak_scenarios: dict[str, Scenario] = {
    name: getattr(scenarios, name)() for name in scenarios.__all__
}


@wf.register(  # type: ignore[misc]
    name="Context leak attempt",
    description="Attempt to leak context from tested LLM model.",
)
def context_leak_chat(ui: UI, params: dict[str, Any]) -> str:
    context_leak_scenario = ui.multiple_choice(
        sender="Context leakage team",
        prompt="Please select the type of context leakage you would like to attempt.",
        choices=list(context_leak_scenarios),
    )

    return context_leak_scenarios[context_leak_scenario].run(ui, params)


@wf.register(  # type: ignore[misc]
    name="Context leak attempt report",
    description="Report on the context leak attempt.",
)
def context_leak_report(ui: UI, params: dict[str, Any]) -> str:
    for scenario in context_leak_scenarios:
        context_leak_scenarios[scenario].report(ui, params)
    return (
        "You can find the reports for all context leak attempts in the messages above."
    )
