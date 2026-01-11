from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get

mcp = FastMCP("mcp_server")

# Tools for searching the web
@mcp_tool()
def web_search(query: str) -> str:
    """Search the web for the information"""
    results = tavily_client.search(query)
    return results

# Resources - Provide access to langchain-ai repo files
@mcp.resources("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """
    Resources for accessing langchain-ai/langchain-mcp-adapter.md file
    """

    url = f"https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md"

    try:
        resp = get(url)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"

# Prompt Template
@mcp.prompt()
def prompt():
    """
    Analyze data from a langchain-ai repo file with comprehensive insights
    """

    return """
You are a helpful assistant that answers user questions about LangChain, LangGraph and LangSmith.

    You can use the following tools/resources to answer user questions:
    - search_web: Search the web for information
    - github_file: Access the langchain-ai repo files

    If the user asks a question that is not related to LangChain, LangGraph or LangSmith, you should say "I'm sorry, I can only answer questions about LangChain, LangGraph and LangSmith."

    You may try multiple tool and resource calls to answer the user's question.

    You may also ask clarifying questions to the user to better understand their question.
"""

if __name__ == "__main__":
    mcp.run(transport="stdio")