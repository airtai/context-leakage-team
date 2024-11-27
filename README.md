# Prompt Leakage Probing

## Overview

The **Prompt Leakage Probing** project provides a framework for testing Large Language Model (LLM) agents for their susceptibility to system prompt leaks. It currently implements two attack strategies:

1. **Simple Attack**: Uses `PromptLeakagePromptGeneratorAgent` and `PromptLeakageClassifier` to attempt prompt extraction.
2. **Base64 Attack**: Encodes sensitive parts of the prompt in Base64 via the Generator for testing the model's ability to decode and potentially leak these parts.

## Prerequisites

Ensure you have the following installed:

- Python >=3.10

## Setup Instructions

### 1. Install the Project

Clone the repository and install the dependencies:

```bash
pip install ."[dev]"
```

### 2. Run the Project Locally

Start the application using the provided script:

```bash
./scripts/run_fastapi_locally.sh
```

This will start the Fastagency FastAPI provider and Mesop provider instances. You can then access the application through your browser.

### 3. Use the Devcontainer (Optional)

The project comes with **Devcontainers** configured, enabling a streamlined development environment setup if you use tools like Visual Studio Code with the Devcontainer extension.

## Application Usage

When you open the application in your browser, you'll find:


## Adding New Agents and Scenarios

### Agents

To add new agents:

- Locate existing agents in `context_leakage_team/workflow/agents/`.
- Implement your new agent as a class inheriting the appropriate base classes.
- Place the implementation in the `agents/` directory.

### Scenarios

To add new scenarios:

- Existing scenarios are organized under `context_leakage_team/workflow/scenarios/`.
- Scenarios are structured by type of attack.
- Add new scenarios as modules within the `scenarios/` directory, ensuring they follow the established structure.

## Folder Structure

Here is the basic folder structure:

```
├── agents
│   ├── prompt_leakage_prompt_generator_agent.py  # Simple attack generator
│   ├── prompt_leakage_classifier.py             # Simple attack classifier
│   ├── base64_leakage_agent.py                  # Base64 attack generator
├── scenarios
│   ├── easy                                     # Easy scenarios
│   ├── medium                                   # Medium scenarios
│   └── hard                                     # Hard scenarios
├── scripts
│   └── run_fastapi_locally.sh                   # Script to start the application locally
├── devcontainer                                 # Devcontainer configuration
├── pyproject.toml                               # Project dependencies
└── README.md                                    # Project documentation
```

## Example Usage

1. Start the FastAPI application:
   ```bash
   ./scripts/run_fastapi_locally.sh
   ```

2. Open your browser and navigate to the application interface.

3. Select a tested model endpoint (Easy, Medium, Hard).

4. Use the provided agents and scenarios to test the model's susceptibility to prompt leakage.

## License

Include your license information here.
