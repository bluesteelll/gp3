import os

from langchain_core.tools import tool
from tavily import TavilyClient

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _client


@tool
def tavily_search(query):
    response = _get_client().search(query, max_results=5)
    return response.get("results", [])
