from pathlib import Path

prompt_path = Path(__file__).parent / "system_prompt_1.md"


def get_prompt(confidential_part: str, not_confidential_part: str, tools: str) -> str:
    return prompt_path.read_text().format(
        confidential_part=confidential_part,
        not_confidential_part=not_confidential_part,
        tools=tools,
    )
