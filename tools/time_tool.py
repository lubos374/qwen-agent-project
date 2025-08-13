# tools/time_tool.py
import json
from datetime import datetime
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool("get_time")
class GetTime(BaseTool):
    """Return current local time as ISO string."""
    description = "Return current local time"
    parameters = []
    def call(self, params: str = None, **kwargs) -> str:
        return json.dumps({"time": datetime.now().isoformat()})