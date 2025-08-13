# multi_agent_system.py
import os
from qwen_agent.agents import Assistant
from qwen_agent.gui import GroupChat

# Import your tool modules so registration runs
import tools.time_tool
import tools.web_search_tool

# --- LLM Configuration (shared by all agents) ---
llm_cfg = {
    "model": "qwen3:1.7b",
    "model_server": "http://localhost:11434/v1",
    "api_key": "EMPTY",
    "generate_cfg": {
        "max_tokens": 1500,
        "temperature": 0.7,
    }
}

# --- RAG Configuration (for the worker) ---
DOCS_PATH = os.path.join(os.path.dirname(__file__), 'docs')
if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)
    with open(os.path.join(DOCS_PATH, 'my_knowledge.txt'), 'w') as f:
        f.write("Lubomir is the creator of this AI agent system. His goal is to build a powerful, automated AI.")

# --- Define the Agents in the Swarm ---

# 1. The Worker Agent: Has all the tools and knowledge.
worker_agent = Assistant(
    name="WorkerAgent",
    llm=llm_cfg,
    function_list=["code_interpreter", "web_search", "get_time"],
    knowledge_base={'source': DOCS_PATH},
    system_message=(
        "You are a diligent worker agent. "
        "Your job is to execute tasks using your tools (code_interpreter, web_search, get_time) and knowledge base. "
        "Perform the specific task you are given and report the result. Do not add extra commentary."
    )
)

# 2. The Planner Agent: The "brains" of the operation.
planner_agent = Assistant(
    name="PlannerAgent",
    llm=llm_cfg,
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
    llm=llm_cfg
)

# --- Main Execution Loop ---
if __name__ == "__main__":
    print("Multi-Agent Swarm is running! Give it a complex task. Type 'exit' to quit.")
    
    # Example of a complex task for the swarm:
    # "Based on the information at 'https://blog.research.google/2024/05/the-next-generation-of-gemini-models/', 
    # what is Project Astra? Then, tell me who created this AI system according to my knowledge base."

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Swarm: Shutting down. Goodbye!")
            break
        
        # The group chat manages the message history
        messages = [{"role": "user", "content": user_input}]
        
        print("\n--- Swarm Activity ---")
        # Stream the multi-agent conversation
        for piece in group.run(messages=messages):
            print(piece)
        print("--- End of Activity ---\n")

