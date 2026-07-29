import httpx

from config import get_settings
from tools import BaseTool

settings = get_settings()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Recherche des informations récentes sur le web via l'API Tavily. "
        "Argument : query (la recherche à effectuer)."
    )
    requires_validation = False

    def run(self, query: str, **kwargs) -> str:
        response = httpx.post(
            TAVILY_SEARCH_URL,
            json={"api_key": settings.tavily_api_key, "query": query, "max_results": 5},
            timeout=15.0,
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            return "Aucun résultat trouvé."

        return "\n\n".join(f"- {item['title']} ({item['url']})\n  {item['content']}" for item in results)
