"""Search Agent - handles web search requests."""

from agent.agents.main_agent import MainAgent
from agent.skills.web_search import WebSearchTool


class SearchAgent:
    """Agent specialized in web search."""

    def __init__(self):
        self.tool = WebSearchTool()

    async def search(self, query: str, max_results: int = 5) -> str:
        """Perform a web search."""
        result = self.tool.execute(query=query, max_results=max_results)
        if result.error:
            return f"搜索出错: {result.error}"
        return result.output
