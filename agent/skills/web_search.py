"""Web search skill using Tavily API."""

from typing import Optional
import os

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

from agent.tools.base import Tool, ToolResult


class WebSearchTool(Tool):
    """Search the web for information."""

    name = "web_search"
    description = "Search the web for information. Use this when you need to find current information or facts."

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key and TavilyClient else None

    def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """Execute a web search."""
        if not self.client:
            return ToolResult(
                output="",
                error="Tavily API key not configured. Set TAVILY_API_KEY environment variable."
            )

        try:
            results = self.client.search(query=query, max_results=max_results)
            formatted = []
            for r in results.get("results", []):
                formatted.append(f"- {r['title']}: {r['url']}\n  {r['content'][:200]}...")
            return ToolResult(output="\n".join(formatted) if formatted else "No results found.")
        except Exception as e:
            return ToolResult(output="", error=str(e))
