import os
import serpapi
import urllib, urllib.request, urllib.parse
from typing import List, Optional
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv(override=True)

def google_search(query: str) -> str:
    """Performs a Google search using SerpApi."""
    try:
        client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })
        
        # Extract snippets from organic results for the LLM to read
        if "organic_results" in results:
            snippets = [
                f"Title: {res.get('title')}\nSnippet: {res.get('snippet')}\nLink: {res.get('link')}"
                for res in results["organic_results"][:5] # Limit to top 5 to save tokens
            ]
            return "\n\n".join(snippets)
        return "No relevant organic results found."
        
    except Exception as e:
        return f"SerpApi Error: {str(e)}"

def search_arxiv(
    query: Optional[str] = None, 
    id_list: Optional[List[str]] = None,
    max_results: int = 5,
    sort_by: str = "relevance",
    sort_order: str = "descending"
) -> List[dict]:
    """
    Search arXiv for papers using a query string or a list of specific IDs.
    
    Args:
        query: Search term (e.g., 'au:del_maestro AND ti:checkerboard'). 
               Supports prefixes: ti (title), au (author), abs (abstract), cat (category).
        id_list: Specific arXiv IDs to retrieve (e.g., ['0703.051', 'hep-ex/0307015']).
        max_results: Number of papers to return (max 2000 per call).
        sort_by: 'relevance', 'lastUpdatedDate', or 'submittedDate'.
        sort_order: 'ascending' or 'descending'.
    """
    base_url = 'http://export.arxiv.org/api/query?'
    params = {
        "search_query": query if query else "",
        "id_list": ",".join(id_list) if id_list else "",
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }
    
    full_url = base_url + urllib.parse.urlencode(params)
    
    with urllib.request.urlopen(full_url) as response:
        content = response.read().decode('utf-8')
        
    root = ET.fromstring(content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    results = []
    for entry in root.findall('atom:entry', ns):
        results.append({
            "title": entry.find('atom:title', ns).text.strip(),
            "id": entry.find('atom:id', ns).text.split('/')[-1],
            "summary": entry.find('atom:summary', ns).text.strip(),
            "authors": [auth.find('atom:name', ns).text for auth in entry.findall('atom:author', ns)],
            "published": entry.find('atom:published', ns).text,
            "pdf_link": entry.find("atom:link[@title='pdf']", ns).attrib['href'] if entry.find("atom:link[@title='pdf']", ns) is not None else ""
        })
    
    return results

async def search_tools():

    return [
        Tool(
            name="search_arxiv",
            func=search_arxiv,
            description=(
                "Search arXiv for academic papers. Use 'query' for keyword/field searches. "
                "Supports field prefixes: 'ti:' (title), 'au:' (author), 'abs:' (abstract), 'cat:' (category). "
                "Supports Boolean logic: 'AND', 'OR', 'ANDNOT'. "
                "Example: 'au:del_maestro AND ti:checkerboard'. "
                "Use 'id_list' for specific paper IDs. 'max_results' defaults to 5. "
                "Sorting: 'sortBy' can be 'relevance' or 'submittedDate'."
            ),
            input_schema={
                "query": str, 
                "id_list": list, 
                "max_results": int, 
                "sort_by": str
            },
            output_schema={"papers": list}
        ),
        Tool(
            name="google_search",
            func=google_search,
            description="Performs a Google search using the Serper API. Useful for finding general news, blog posts, or context outside of academic papers.",
            input_schema={"query": str},
            output_schema={"results": list}
        )
    ]