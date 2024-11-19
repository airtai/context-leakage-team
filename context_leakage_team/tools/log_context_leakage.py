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
    save_path: Path, model_name: str
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
            "model_name": model_name,
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
    """Parses the log CSV file and generates a Markdown summary report with a combined table for all models.

    Parameters:
    - log_path (Path): Path to the CSV log file.
    - success_threshold (int): Minimum leakage level to count as a 'successful' leakage.

    Returns:
    - str: A Markdown formatted string with detailed reporting.
    """
    import pandas as pd

    # Load the log data from the CSV file
    try:
        df = pd.read_csv(log_path)
    except FileNotFoundError:
        return "Log file not found. Please ensure the log path is correct."
    except pd.errors.EmptyDataError:
        return "Log file is empty. Please provide a valid log file."

    if "model_name" not in df.columns:
        return "The log file is missing the required 'model_name' column."

    # Group data by model_name
    grouped = df.groupby("model_name")

    # Initialize the overall report
    markdown_report = "# Context Leakage Test Report\n\n"

    # Create a summary table for all models
    markdown_report += "## Leakage Level Summary Table\n\n"
    markdown_report += (
        "| Model Name   | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |\n"
    )
    markdown_report += (
        "|--------------|---------|---------|---------|---------|---------|\n"
    )

    for model_name, group in grouped:
        leakage_counts = group["leakage_level"].value_counts()
        row = [
            f"{leakage_counts.get(level, 0)}" for level in range(5)
        ]  # Ensure counts for all levels
        markdown_report += f"| {model_name:<12} | {' | '.join(row)} |\n"

    # Add detailed breakdown for each model
    markdown_report += "\n## Detailed Reports per Model\n\n"

    for model_name, group in grouped:
        # Basic statistics
        total_attempts = len(group)
        successful_attempts = group[group["leakage_level"] >= success_threshold].shape[
            0
        ]
        success_rate = (
            (successful_attempts / total_attempts) * 100 if total_attempts > 0 else 0
        )

        # Distribution of context leakage levels
        leakage_distribution = group["leakage_level"].value_counts().sort_index()

        # Add model-specific header
        markdown_report += f"### Model: {model_name}\n\n"
        markdown_report += f"**Total Attempts**: {total_attempts}\n\n"
        markdown_report += f"**Successful Attempts** (Leakage level >= {success_threshold}): {successful_attempts} ({success_rate:.2f}%)\n\n"

        # Success board
        markdown_report += "#### Success Board\n\n"
        level_emojis = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴", 4: "🔥"}
        for level in range(5):
            count = leakage_distribution.get(level, 0)
            emoji = level_emojis.get(level, "❓")
            markdown_report += f"- Level {level} ({emoji}): {count} occurrences\n"

        # Summary of leakage level distribution
        markdown_report += "\n#### Leakage Level Distribution\n\n"
        markdown_report += "| Leakage Level | Count |\n"
        markdown_report += "|---------------|-------|\n"
        for level, count in leakage_distribution.items():
            markdown_report += f"| {level}             | {count}   |\n"

        # Adding a visually pleasing list of successful prompts and responses
        successful_prompts = group[group["leakage_level"] >= success_threshold][
            ["prompt", "result"]
        ]
        if not successful_prompts.empty:
            markdown_report += "\n#### List of Successful Prompts and Responses\n"
            markdown_report += (
                "\nBelow is a detailed list of successful prompts and their responses, "
                "highlighting effective context leakage detections.\n\n"
            )

            for index, row in successful_prompts.iterrows():
                markdown_report += f"##### 📝 Prompt {index + 1}\n"
                markdown_report += f"- **Prompt Text**:\n\n    > {row['prompt']}\n\n"  # type: ignore[call-overload]
                markdown_report += (
                    f"- **Detected Response**:\n\n    > {row['result']}\n\n"  # type: ignore[call-overload]
                )
                markdown_report += "---\n"

    return markdown_report
