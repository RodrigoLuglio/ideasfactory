"""
Web search tool for IdeasFactory agents.

This module provides utilities for searching the web and extracting relevant information.
"""

import os
import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Union
from bs4 import BeautifulSoup
import json

# Configure logging
logger = logging.getLogger(__name__)

# Default API configuration
DEFAULT_SEARCH_API_KEY = os.environ.get("IDEASFACTORY_SEARCH_API_KEY", "")
DEFAULT_SEARCH_ENGINE_ID = os.environ.get("IDEASFACTORY_SEARCH_ENGINE_ID", "")


async def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for information.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results with title, link, and snippet
    """
    # Use Google Custom Search API if available
    if DEFAULT_SEARCH_API_KEY and DEFAULT_SEARCH_ENGINE_ID:
        return await _google_search(query, num_results)
    
    # Fall back to a less API-dependent method
    return await _fallback_search(query, num_results)


async def _google_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search using Google Custom Search API.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": DEFAULT_SEARCH_API_KEY,
        "cx": DEFAULT_SEARCH_ENGINE_ID,
        "q": query,
        "num": min(num_results, 10)  # API limit is 10 per request
    }
    
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
                                "snippet": item.get("snippet", ""),
                                "source": "google"
                            })
                    
                    return results
                else:
                    logger.error(f"Google Search API error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error in Google search: {str(e)}")
        return []


async def _fallback_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fallback search method using another search engine or service.
    This could be replaced with another search API or service like DuckDuckGo.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    # Using DuckDuckGo as fallback (this is a simplified implementation)
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    results = []
                    result_elements = soup.select(".result")[:num_results]
                    
                    for element in result_elements:
                        title_elem = element.select_one(".result__title")
                        link_elem = element.select_one(".result__url")
                        snippet_elem = element.select_one(".result__snippet")
                        
                        title = title_elem.text.strip() if title_elem else ""
                        link = link_elem.text.strip() if link_elem else ""
                        snippet = snippet_elem.text.strip() if snippet_elem else ""
                        
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "source": "duckduckgo"
                        })
                    
                    return results
                else:
                    logger.error(f"DuckDuckGo search error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error in fallback search: {str(e)}")
        return []


async def scrape_webpage(url: str) -> Optional[Dict[str, Any]]:
    """
    Scrape content from a webpage.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with title, content, and metadata
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Get the title
                    title = soup.title.text.strip() if soup.title else ""
                    
                    # Get the main content
                    # This is a simple implementation and might need refinement
                    # depending on the structure of the websites being scraped
                    content = ""
                    
                    # Try to find the main content
                    main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
                    
                    if main_content:
                        # Extract text from paragraphs
                        paragraphs = main_content.find_all("p")
                        content = "\n".join([p.text.strip() for p in paragraphs])
                    else:
                        # Fallback to all paragraphs
                        paragraphs = soup.find_all("p")
                        content = "\n".join([p.text.strip() for p in paragraphs])
                    
                    # Extract metadata
                    metadata = {}
                    meta_tags = soup.find_all("meta")
                    for tag in meta_tags:
                        if tag.get("name") and tag.get("content"):
                            metadata[tag["name"]] = tag["content"]
                    
                    return {
                        "title": title,
                        "content": content,
                        "url": url,
                        "metadata": metadata
                    }
                else:
                    logger.error(f"Error scraping {url}: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None