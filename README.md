# Prompt Leakage Probing

## Overview

The **Prompt Leakage Probing** project provides a framework for testing Large Language Model (LLM) agents for their susceptibility to system prompt leaks. It currently implements two attack strategies:

1. **Simple Attack**: Uses `ContextLeakagePromptGeneratorAgent` and `ContextLeakageClassifierAgent` to attempt prompt extraction.
2. **Base64 Attack**: Enables `ContextLeakagePromptGeneratorAgent` to encode sensitive parts of the prompt in Base64 to bypass sensitive prompt detection.

## Prerequisites

Ensure you have the following installed:

- Python >=3.10

Additionally, ensure that your `OPENAI_API_KEY` is exported to your environment.

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

![Workflow selection](imgs/workflow_selection.png?raw=true "Workflow selection")

### Running the Tests

After selecting **"Attempt to leak context from selected LLM model"**, you will start a workflow for probing the LLM for context leakage. During this process, you will:

1. Select the prompt leakage scenario you want to test.
2. Choose the model you want to test.
3. Specify the number of attempts to leak the context in the chat.

![Test configuration](imgs/configuring_testing.png?raw=true "Test configuration")

The `ContextLeakagePromptGeneratorAgent` will then generate adversarial prompts aimed at making the tested agent leak its prompt. After each response from the tested agent, the `ContextLeakageClassifierAgent` will analyze the response and report the level of context leakage.

Prompt generation:
![Prompt generation](imgs/prompt_generation.png?raw=true "Prompt generation")

Tested agent response:
![Tested agent response](imgs/tested_agent_response.png?raw=true "Tested agent response")

Response classification:
![Response classification](imgs/response_classification.png?raw=true "Response classification")

All response classifications are saved as CSV files in the `reports` folder. These files contain the prompt, response, reasoning, and leakage level. They are used to display the reports flow, which we will now demonstrate.

### Displaying the Reports

In the workflow selection screen, select **"Report on the context leak attempt"**.
This workflow provides a detailed report for each context leakage scenario and model combination that has been tested.

![Report flow](imgs/report_flow.png?raw=true "Report flow")

## Tested Models

The project includes three tested model endpoints that are started alongside the service. These endpoints are used to demonstrate the context leakage workflow and can be accessed through predefined routes. The source code for these models is located in the `tested_chatbots` folder.

### Description of Tested Models

| **Model** | **Description**                                                                                          | **Endpoint**   |
|-----------|----------------------------------------------------------------------------------------------------------|----------------|
| Easy      | Uses a basic prompt without any hardening techniques. No canary words are included, and no LLM guardrail is applied. | `/low`         |
| Medium    | Applies prompt hardening techniques to improve robustness over the easy model but still lacks canary words or guardrail. | `/medium`      |
| Hard      | Combines prompt hardening with the addition of canary words and the use of a guardrail for better protection. | `/high`        |

### Implementation Details

The endpoints for these models are defined in the `tested_chatbots/chatbots_router` file. They are part of the FastAPI provider and are available under the following paths:

- `/low`: Easy model endpoint.
- `/medium`: Medium model endpoint.
- `/high`: Hard model endpoint.

These endpoints demonstrate different levels of susceptibility to prompt leakage and serve as examples to test the implemented agents and scenarios.
