# Qwen Agent Swarm

This project demonstrates a simple yet powerful AI agent system built using the `qwen-agent` library. It includes two main modes of operation: a single, general-purpose assistant and a multi-agent "swarm" that uses a Planner-Worker pattern.

## Features

- **Single Agent Mode (`agent.py`):** A standalone assistant that can use tools and a knowledge base to answer questions.
- **Multi-Agent Swarm (`multi_agent_system.py`):** A more advanced setup where a `PlannerAgent` decomposes tasks and a `WorkerAgent` executes them using a suite of tools.
- **Tools:**
  - `web_search`: Fetches content from a URL.
  - `get_time`: Returns the current time.
  - `code_interpreter`: Executes Python code in a sandboxed environment.
- **RAG (Retrieval-Augmented Generation):** The agents can draw from a local knowledge base stored in the `docs` directory.
- **Local LLM Support:** Configured to use a local LLM via Ollama.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your LLM:**
    This project is configured to use a local LLM served by [Ollama](https://ollama.ai/).
    - Install Ollama.
    - Pull the `qwen:1.8b` model:
      ```bash
      ollama pull qwen:1.8b
      ```
    - Ensure the Ollama server is running.

4.  **(Optional) Add to the Knowledge Base:**
    - Place any `.txt` or `.md` files into the `docs` directory. The agents will automatically be able to access the information within them.

## How to Run

### Single Agent

To run the single assistant:
```bash
python agent.py
```

### Multi-Agent Swarm

To run the multi-agent swarm:
```bash
python multi_agent_system.py
```

By default, the swarm will only show the final, synthesized response. To see the full conversation between the Planner and Worker agents, use the `--verbose` flag:
```bash
python multi_agent_system.py --verbose
```
