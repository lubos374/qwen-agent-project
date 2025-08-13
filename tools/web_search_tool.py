# tools/web_search_tool.py
import requests
from bs4 import BeautifulSoup
from qwen_agent.tools.base import register_tool

# It's good practice to define the tool's name explicitly
TOOL_NAME = "web_search"

@register_tool(TOOL_NAME)
def web_search(url: str):
    """
    Fetches the text content from a given URL.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        A dictionary with the status and the extracted text content or an error message.
    """
    try:
        print(f"Attempting to search URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Use BeautifulSoup to parse the HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Truncate for brevity to avoid overwhelming the context window
        max_length = 4000
        if len(text) > max_length:
            text = text[:max_length] + "\n... (content truncated)"

        return {"status": "success", "content": text}

    except requests.RequestException as e:
        return {"status": "error", "message": f"Failed to fetch URL: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

