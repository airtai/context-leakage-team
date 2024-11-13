from pathlib import Path
from typing import Callable

import pandas as pd
from pydantic import BaseModel, Field


class LogContextLeakageInput(BaseModel):
    """Model for input parameters required for logging context leakage detection results."""

    prompt: str = Field(
        ...,
        description="The prompt text that was used to test context leakage in the LLM.",
    )
    result: str = Field(
        ...,
        description="The outcome or response produced by the LLM after using the prompt.",
    )
    reasoning: str = Field(
        ...,
        description="Explanation or reasoning behind the detected level of context leakage.",
    )
    leakage_level: int = Field(
        ...,
        description="An integer between 0 and 4 representing the severity of context leakage detected.",
    )


def create_log_context_leakage_function(
    save_path: Path,
) -> Callable[[LogContextLeakageInput], LogContextLeakageInput]:
    """Factory to create a logging function with a fixed save path for context leakage results.

    Parameters:
    - save_path (str): The file path where the log DataFrame will be saved.

    Returns:
    - function: A function that logs context leakage data to the specified path.
    """

    def log_context_leakage(data: LogContextLeakageInput) -> LogContextLeakageInput:
        # Define the save path as a Path object for cross-platform compatibility
        file_path = save_path

        # Create a DataFrame row from the input data
        row = {
            "prompt": data.prompt,
            "result": data.result,
            "reasoning": data.reasoning,
            "leakage_level": data.leakage_level,
        }

        # Check if the DataFrame file already exists
        if file_path.exists():
            # Load existing DataFrame and append the new row
            df = pd.read_csv(file_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            # Create a new DataFrame
            df = pd.DataFrame([row])

        # Save the updated DataFrame back to the same path
        df.to_csv(file_path, index=False)

        return data

    return log_context_leakage


def generate_markdown_report(log_path: Path, success_threshold: int = 1) -> str:
    """Parses the log CSV file and generates a Markdown summary report.

    Parameters:
    - log_path (str): Path to the CSV log file.
    - success_threshold (int): Minimum leakage level to count as a 'successful' leakage.

    Returns:
    - str: A Markdown formatted string with detailed reporting.
    """
    # Load the log data from the CSV file
    try:
        df = pd.read_csv(log_path)
    except FileNotFoundError:
        return "Log file not found. Please ensure the log path is correct."

    # Basic statistics
    total_attempts = len(df)
    successful_attempts = df[df["leakage_level"] >= success_threshold].shape[0]
    success_rate = (
        (successful_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    )

    # Distribution of context leakage levels
    leakage_distribution = df["leakage_level"].value_counts().sort_index()

    # Markdown report generation
    markdown_report = "# Context Leakage Test Report\n\n"
    markdown_report += f"**Total Attempts**: {total_attempts}\n\n"
    markdown_report += f"**Successful Attempts** (Leakage level >= {success_threshold}): {successful_attempts} ({success_rate:.2f}%)\n\n"

    # Success board
    markdown_report += "## Success Board\n\n"
    level_emojis = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴", 4: "🔥"}
    for level in range(5):
        count = leakage_distribution.get(level, 0)
        emoji = level_emojis.get(level, "❓")
        markdown_report += f"- Level {level} ({emoji}): {count} occurrences\n"

    # Summary of leakage level distribution
    markdown_report += "\n## Leakage Level Distribution\n\n"
    markdown_report += "| Leakage Level | Count |\n"
    markdown_report += "|---------------|-------|\n"
    for level, count in leakage_distribution.items():
        markdown_report += f"| {level}             | {count}   |\n"

    # Adding a visually pleasing list of successful prompts and responses
    successful_prompts = df[df["leakage_level"] >= success_threshold][
        ["prompt", "result"]
    ]
    if not successful_prompts.empty:
        markdown_report += "\n## List of Successful Prompts and Responses\n"
        markdown_report += "\nBelow is a detailed list of successful prompts and their responses, highlighting effective context leakage detections.\n\n"

        for index, row in successful_prompts.iterrows():
            markdown_report += f"### 📝 Prompt {index + 1}\n"
            markdown_report += f"- **Prompt Text**:\n\n    > {row['prompt']}\n\n"
            markdown_report += f"- **Detected Response**:\n\n    > {row['result']}\n\n"
            markdown_report += "---\n"

    return markdown_report
