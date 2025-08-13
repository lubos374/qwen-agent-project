# agent_v2.py
import os
from qwen_agent.agents import Assistant

# Import your tool modules so registration runs
import tools.time_tool  # noqa: F401
import tools.web_search_tool # noqa: F401

# --- LLM Configuration ---
# Using your local Ollama setup
llm_cfg = {
    "model": "qwen3:1.7b",
    "model_server": "http://localhost:11434/v1",
    "api_key": "EMPTY",
    "generate_cfg": {
        "max_tokens": 1024, # Increased tokens for potentially larger RAG context
        "temperature": 0.7,
    }
}

# --- Tool Configuration ---
# Add your new web_search tool to the list
tools_list = ["get_time", "code_interpreter", "web_search"]

# --- RAG Configuration ---
# Point to the directory containing your knowledge base files
# Create a 'docs' folder in your project and add some .txt or .md files.
DOCS_PATH = os.path.join(os.path.dirname(__file__), 'docs')
if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)
    # Create a dummy file for demonstration if the folder is new
    with open(os.path.join(DOCS_PATH, 'my_knowledge.txt'), 'w') as f:
        f.write("Lubomir is the creator of this AI agent system. He is building an AI god.")

# --- Agent Initialization ---
# Initialize the assistant with the LLM, tools, and knowledge base
bot = Assistant(
    llm=llm_cfg,
    function_list=tools_list,
    knowledge_base={'source': DOCS_PATH}, # Enable RAG here
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

