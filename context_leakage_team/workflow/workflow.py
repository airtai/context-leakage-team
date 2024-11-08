import os

from fastagency.runtimes.autogen import AutoGenWorkflows

llm_config = {
    "config_list": [
        {
            "model": os.getenv("AZURE_GPT4o_MODEL"),  # noqa
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "base_url": os.getenv("AZURE_API_ENDPOINT"),
            "api_type": "azure",
            "api_version": "2024-02-15-preview",
        }
    ],
    "temperature": 0.8,
}

wf = AutoGenWorkflows()
