# multi_agent_system.py
import os
import json
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from qwen_agent.agents import Assistant
from qwen_agent.gui import GroupChat
from qwen_agent.tools.base import BaseTool, register_tool
from config import LLM_CFG, TOOLS_LIST

@register_tool("get_time")
class GetTime(BaseTool):
    """Return current local time as ISO string."""
    description = "Return current local time"
    parameters = []
    def call(self, params: str = None, **kwargs) -> str:
        return json.dumps({"time": datetime.now().isoformat()})

@register_tool("web_search")
class WebSearch(BaseTool):
    """
    Fetches the text content from a given URL asynchronously.
    """
    description = "Fetches the text content from a given URL."
    parameters = [{
        "name": "url",
        "type": "string",
        "description": "The URL to fetch content from.",
        "required": True
    }]

    async def call(self, params: str, **kwargs) -> str:
        """
        Fetches the text content from a given URL asynchronously.

        Args:
            params (str): A JSON string containing the 'url'.

        Returns:
            A JSON string with the status and the extracted text content or an error message.
        """
        try:
            params = json.loads(params)
            url = params['url']

            print(f"Attempting to search URL: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            max_length = 4000
            if len(text) > max_length:
                text = text[:max_length] + "\n... (content truncated)"

            return json.dumps({"status": "success", "content": text})

        except httpx.RequestError as e:
            return json.dumps({"status": "error", "message": f"Failed to fetch URL: {e}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

# --- RAG Configuration ---
DOCS_PATH = os.path.join(os.path.dirname(__file__), 'docs')
if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)

doc_files = [os.path.join(DOCS_PATH, f) for f in os.listdir(DOCS_PATH) if os.path.isfile(os.path.join(DOCS_PATH, f))]


# --- Define the Agents in the Swarm ---

# 1. The Worker Agent: Has all the tools and knowledge.
worker_agent = Assistant(
    name="WorkerAgent",
    llm=LLM_CFG,
    function_list=TOOLS_LIST,
    files=doc_files,
    system_message=(
        "You are a diligent worker agent. "
        "Your job is to execute tasks using your tools (code_interpreter, web_search, get_time) and knowledge base. "
        "Perform the specific task you are given and report the result. Do not add extra commentary."
    )
)

# 2. The Planner Agent: The "brains" of the operation.
planner_agent = Assistant(
    name="PlannerAgent",
    llm=LLM_CFG,
    system_message=(
        "You are the master planner. Your role is to communicate with the user and coordinate the worker. "
        "1. Understand the user's request. "
        "2. Break it down into a clear, step-by-step plan. "
        "3. Instruct the WorkerAgent to execute one step at a time. "
        "4. When all steps are complete, synthesize the results and give the final answer to the user. "
        "You do not have tools yourself; you must delegate all actions to the WorkerAgent."
    )
)

# --- Set up the Group Chat ---
# This orchestrates the conversation between the agents
all_agents = [planner_agent, worker_agent]
group = GroupChat(
    agents=all_agents,
    llm=LLM_CFG
)

# --- Main Execution Loop ---
if __name__ == "__main__":
    import sys
    # Check for a verbose flag
    verbose = "--verbose" in sys.argv
    
    print("Multi-Agent Swarm is running! Give it a complex task. Type 'exit' to quit.")
    print("Use the --verbose flag to see the full agent conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Swarm: Shutting down. Goodbye!")
            break
        
        messages = [{"role": "user", "content": user_input}]
        
        final_response = ""
        print("\nSwarm response:")
        if verbose:
            print("--- Swarm Activity ---")
            for piece in group.run(messages=messages):
                print(piece, end="", flush=True)
                final_response += str(piece)
            print("\n--- End of Activity ---\n")
        else:
            # Silently run the group and capture the final response
            full_conversation = list(group.run(messages=messages))
            if full_conversation:
                # The last message in the conversation is usually the planner's summary
                final_response = full_conversation[-1]
                # The response might be a dict, so extract content if so
                if isinstance(final_response, dict) and 'content' in final_response:
                    print(final_response['content'])
                else:
                    print(final_response)
            else:
                print("The swarm did not produce a response.")
        print("\n")

