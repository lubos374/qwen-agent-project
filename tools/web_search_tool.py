# tools/web_search_tool.py
import httpx
import json
from bs4 import BeautifulSoup
from qwen_agent.tools.base import BaseTool, register_tool

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

