"""
Enhanced web search tool for specialized research agents.

This module extends the basic web search capabilities to provide
more advanced search options while preserving agent autonomy.
"""

import os
import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Union, Set
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urlparse
import hashlib
from datetime import datetime, timedelta

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.tools.web_search import search_web, scrape_webpage

# Configure logging
logger = logging.getLogger(__name__)

# Simple result cache
_search_cache = {}


@handle_errors
def clear_cache() -> None:
    """Clear the search result cache."""
    global _search_cache
    _search_cache = {}


@handle_async_errors
async def search_custom(
    query: str,
    search_engine: str = "google",
    num_results: int = 10,
    cache_hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Perform a search using a specific search engine with customizable parameters.
    
    Args:
        query: Search query
        search_engine: Search engine to use (google, github, stackoverflow, arxiv)
        num_results: Number of results to return
        cache_hours: Number of hours to cache results
        
    Returns:
        List of search results
    """
    # Generate cache key
    cache_key = f"{search_engine}:{query}:{num_results}"
    hash_obj = hashlib.md5(cache_key.encode())
    cache_id = hash_obj.hexdigest()
    
    # Check cache
    if cache_id in _search_cache:
        cache_entry = _search_cache[cache_id]
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        if datetime.now() - cache_time < timedelta(hours=cache_hours):
            return cache_entry["results"]
    
    # Perform search based on engine
    if search_engine == "google":
        results = await search_web(query, num_results)
    elif search_engine == "github":
        results = await _search_github(query, num_results)
    elif search_engine == "stackoverflow":
        results = await _search_stackoverflow(query, num_results)
    elif search_engine == "arxiv":
        results = await _search_arxiv(query, num_results)
    else:
        # Default to standard web search
        results = await search_web(query, num_results)
    
    # Cache results
    _search_cache[cache_id] = {
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    return results


@handle_async_errors
async def _search_github(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search GitHub repositories.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    base_url = "https://api.github.com/search/repositories"
    github_token = os.environ.get("GITHUB_API_TOKEN", "")
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(num_results, 30)  # API limit is 30 per request
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    if "items" in data:
                        for item in data["items"]:
                            results.append({
                                "title": item.get("full_name", ""),
                                "link": item.get("html_url", ""),
                                "snippet": item.get("description", ""),
                                "stars": item.get("stargazers_count", 0),
                                "language": item.get("language", ""),
                                "source": "github"
                            })
                    
                    return results
                else:
                    logger.error(f"GitHub API error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error in GitHub search: {str(e)}")
        return []


@handle_async_errors
async def _search_stackoverflow(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search StackOverflow questions.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    base_url = "https://api.stackexchange.com/2.3/search/advanced"
    stackoverflow_key = os.environ.get("STACKOVERFLOW_API_KEY", "")
    
    params = {
        "q": query,
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": min(num_results, 30)  # API limit is 30 per request
    }
    
    if stackoverflow_key:
        params["key"] = stackoverflow_key
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    if "items" in data:
                        for item in data["items"]:
                            results.append({
                                "title": item.get("title", ""),
                                "link": item.get("link", ""),
                                "snippet": item.get("excerpt", ""),
                                "score": item.get("score", 0),
                                "answers": item.get("answer_count", 0),
                                "source": "stackoverflow"
                            })
                    
                    return results
                else:
                    logger.error(f"StackOverflow API error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error in StackOverflow search: {str(e)}")
        return []


@handle_async_errors
async def _search_arxiv(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search arXiv papers.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": min(num_results, 30)  # API limit is 30 per request
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    
                    # Parse XML
                    soup = BeautifulSoup(xml_data, "xml")
                    entries = soup.find_all("entry")
                    
                    results = []
                    for entry in entries:
                        title_elem = entry.find("title")
                        summary_elem = entry.find("summary")
                        link_elem = entry.find("id")
                        
                        title = title_elem.text.strip() if title_elem else ""
                        summary = summary_elem.text.strip() if summary_elem else ""
                        link = link_elem.text.strip() if link_elem else ""
                        
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": summary[:200] + "..." if len(summary) > 200 else summary,
                            "source": "arxiv"
                        })
                    
                    return results
                else:
                    logger.error(f"arXiv API error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error in arXiv search: {str(e)}")
        return []


@handle_async_errors
async def fetch_full_page(url: str, include_html: bool = False) -> Optional[Dict[str, Any]]:
    """
    Fetch the complete content of a webpage with minimal processing.
    
    Args:
        url: URL to fetch
        include_html: Whether to include the raw HTML in the response
        
    Returns:Z
        Dictionary with complete webpage content
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Get the title
                    title = soup.title.text.strip() if soup.title else ""
                    
                    # Extract all text content - preserving structure
                    all_text = []
                    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                        text = element.text.strip()
                        if text:
                            all_text.append(text)
                    
                    # Extract all links
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        text = link.text.strip()
                        if href and text:
                            links.append({"url": href, "text": text})
                    
                    # Extract metadata
                    metadata = {}
                    meta_tags = soup.find_all("meta")
                    for tag in meta_tags:
                        if tag.get("name") and tag.get("content"):
                            metadata[tag["name"]] = tag["content"]
                    
                    result = {
                        "title": title,
                        "content": "\n".join(all_text),
                        "links": links,
                        "url": url,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Include raw HTML if requested
                    if include_html:
                        result["html"] = html
                    
                    return result
                else:
                    logger.error(f"Error fetching {url}: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None


@handle_async_errors
async def fetch_multiple_pages(urls: List[str], include_html: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Fetch multiple webpages in parallel.
    
    Args:
        urls: List of URLs to fetch
        include_html: Whether to include the raw HTML in the responses
        
    Returns:
        Dictionary mapping URLs to their content
    """
    tasks = [fetch_full_page(url, include_html) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Combine results
    content_map = {}
    for i, result in enumerate(results):
        if result:  # Check if fetching was successful
            content_map[urls[i]] = result
    
    return content_map


@handle_async_errors
async def search_and_fetch(
    query: str, 
    num_results: int = 5, 
    search_engine: str = "google"
) -> Dict[str, Any]:
    """
    Perform a search and fetch the full content of the resulting pages.
    
    Args:
        query: Search query
        num_results: Number of search results to fetch
        search_engine: Search engine to use
        
    Returns:
        Dictionary with search results and their full content
    """
    # First perform the search
    search_results = await search_custom(
        query=query,
        search_engine=search_engine,
        num_results=num_results
    )
    
    if not search_results:
        return {
            "query": query,
            "results": [],
            "content": {}
        }
    
    # Extract URLs from search results
    urls = [result["link"] for result in search_results if "link" in result]
    
    # Fetch the content of each URL
    content = await fetch_multiple_pages(urls)
    
    return {
        "query": query,
        "results": search_results,
        "content": content
    }