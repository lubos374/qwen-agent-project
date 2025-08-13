# config.py
import os

# --- LLM Configuration ---
LLM_CFG = {
    "model": "qwen3:1.7b",
    "model_server": "http://localhost:11434/v1",
    "api_key": "EMPTY",
    "generate_cfg": {
        "max_tokens": 1500,
        "temperature": 0.7,
    }
}


# --- Tool Configuration ---
TOOLS_LIST = ["get_time", "code_interpreter", "web_search"]
