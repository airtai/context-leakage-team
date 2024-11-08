from context_leakage_team.workflow.base64_context_leak import base64_context_leaking
from context_leakage_team.workflow.simple_context_leak import context_leaking
from context_leakage_team.workflow.workflow import wf

wf.register(
    name="Context leak attempt", description="Attempt to leak context from tested LLM."
)(context_leaking)

wf.register(
    name="Base64 context leak attempt",
    description="Attempt to leak context from tested LLM using base 64 encoding of sensitive information",
)(base64_context_leaking)

__all__ = ["wf"]
