# Prompt Leakage Probing

## Overview

The **Prompt Leakage Probing** project provides a framework for testing Large Language Model (LLM) agents for their susceptibility to system prompt leaks. It currently implements two attack strategies:

1. **Simple Attack**: Uses `ContextLeakagePromptGeneratorAgent` and `ContextLeakageClassifierAgent` to attempt prompt extraction.
2. **Base64 Attack**: Enables `ContextLeakagePromptGeneratorAgent` to encode sensitive parts of the prompt in Base64 to avoid sensitive prompt detection.

## Prerequisites

Ensure you have the following installed:

- Python >=3.10

Ensure that you have your `OPENAI_API_KEY` exported to your environment.

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

When you open the application in your browser, you'll first see the workflow selection screen.

![Workflow selection](relative%20imgs/workflow_selection.png?raw=true "Workflow selection")

### Running the tests

Select the "Attempt to leak context from selected LLM model".

Select the prompt leakage scenario you would like to test.

Select the model you would like to test.

Select how many attempts to leak the context will be made in this chat.

Now, the `ContextLeakagePromptGeneratorAgent` will start to generate adversial prompts with a goal of making the tested Agent leak its prompt. After each response from the tested Agent, the `ContextLeakageClassifierAgent` will analyse the response and report the level of contect leakage.

### Showing the reports

Select the "Report on the context leak attempt".

## Tested models
