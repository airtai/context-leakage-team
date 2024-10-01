# context-leakage-team

## Overview
This project focuses on testing machine learning models while ensuring data confidentiality and preventing context leakage. You will need to configure the tested model and manage confidential and non-confidential information before running the context leakage detection tool.

## Prerequisites

Before proceeding, ensure the following:

- Python >=3.10 installed

## Setup Instructions

### 1. Clone the Repository

\```bash
git clone https://github.com/airtai/context-leakage-team.git
cd context-leakage-team
\```

### 2. Install Dependencies

Install the required Python packages:

\```bash
pip install ."[dev]"
\```

### 3. Configure the Model API

Before running the tool, you must configure the model's API settings in `tested_model_config/tested_model_api_config.json`.

Example JSON configuration:

\```json
{
    "url": "your model url",
    "token": "your token"
}
\```

- `url`: The URL where your model is accessible (such as an API endpoint).
- `token`: The access token required to authenticate requests to the model API.

### 4. Add Confidential and Non-Confidential Model Information

- **Confidential Part**: Add the confidential information related to your tested model in the `tested_model_config/tested_model_confidential.md` file.

- **Non-Confidential Part**: Add the non-confidential information of your tested model in the `tested_model_config/tested_model_non_confidential.md` file.

### 5. Run the Context Leakage Detection Team

Once the model configuration is set and the confidential/non-confidential parts are in place, you can run the context leakage detection tool using the following command:

\```bash
fastagency run context_leakage_team/context_leakage_team.py
\```

## Folder Structure

This is the basic folder structure, most of the non important files are omitted for simplicity of the overview.

\```
├── tested_model_config
│   ├── tested_model_api_config.json         # Model API configuration file
│   ├── tested_model_confidential.md         # Confidential model information
│   └── tested_model_non_confidential.md     # Non-confidential model information
├── context_leakage_team
│   └── context_leakage_team.py              # Script to run context leakage detection
├── pyproject.toml                           # List of dependencies
└── README.md                                # Project documentation
\```

## Example Usage

1. Ensure that your `tested_model_api_config.json` is correctly configured with the model URL and token.
2. Place the confidential and non-confidential information in their respective files.
3. Run the context leakage detection:

\```bash
fastagency run context_leakage_team/context_leakage_team.py
\```

This will analyze the model configuration for potential context leaks.

## License

Include your license information here.
