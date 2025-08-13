# agent.py
import os
import json
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from config import LLM_CFG, TOOLS_LIST

@register_tool("get_time")
class GetTime(BaseTool):
    """Return current local time as ISO string."""
    description = "Return current local time"
    parameters = []
    def call(self, params: str = None, **kwargs) -> str:
        return json.dumps({"time": datetime.now().isoformat()})

# --- RAG Configuration ---

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

DOCS_PATH = os.path.join(os.path.dirname(__file__), 'docs')
if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)

doc_files = [os.path.join(DOCS_PATH, f) for f in os.listdir(DOCS_PATH) if os.path.isfile(os.path.join(DOCS_PATH, f))]

# --- Agent Initialization ---
# Initialize the assistant with the LLM, tools, and knowledge base
bot = Assistant(
    llm=LLM_CFG,
    function_list=TOOLS_LIST,
    files=doc_files,
    name="Lubomir-Upgraded-Agent",
    system_message=(
        "You are a helpful AI assistant. "
        "Reply in a concise and professional manner. "
        "Use your available tools (code_interpreter, web_search, get_time) when they are helpful. "
        "You can also access a local knowledge base to answer questions."
    )
)

# --- Main Execution Loop ---
if __name__ == "__main__":
    print("Upgraded Agent is running! Ask me anything. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Bot: Goodbye!")
            break
        
        # The agent needs messages in a specific format
        messages = [{"role": "user", "content": user_input}]
        
        print("\nBot response:")
        # Stream the response
        full_response = ""
        for piece in bot.run(messages=messages):
            print(piece, end="", flush=True)
            full_response += str(piece)
        print("\n---")

