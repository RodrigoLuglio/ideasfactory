"""
Data analysis tool for IdeasFactory agents.

This module provides utilities for analyzing data from various sources.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import json
import re
from collections import Counter, defaultdict

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)

@handle_errors
def extract_key_phrases(text: str, min_count: int = 2) -> List[str]:
    """
    Extract key phrases from text.
    
    Args:
        text: Text to analyze
        min_count: Minimum number of occurrences to consider
        
    Returns:
        List of key phrases
    """
    # Tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
        'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
        'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
        'to', 'from', 'in', 'on', 'at', 'by', 'with'
    }
    
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    
    # Count occurrences
    word_counts = Counter(filtered_words)
    
    # Extract key phrases (words that appear frequently)
    key_phrases = [word for word, count in word_counts.items() if count >= min_count]
    
    return key_phrases


@handle_errors
def summarize_content(text: str, max_sentences: int = 5) -> str:
    """
    Generate a summary of the content.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum number of sentences in the summary
        
    Returns:
        Summarized text
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= max_sentences:
        return text
    
    # Rank sentences by importance
    # This is a simple implementation that considers sentence position
    # and presence of key phrases
    
    key_phrases = extract_key_phrases(text)
    
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        # Position score (first and last sentences are often important)
        position_score = 1.0
        if i == 0 or i == len(sentences) - 1:
            position_score = 2.0
        
        # Content score (sentences with key phrases are important)
        content_score = 0.0
        for phrase in key_phrases:
            if phrase.lower() in sentence.lower():
                content_score += 1.0
        
        # Combine scores
        total_score = position_score + content_score
        sentence_scores.append((i, total_score))
    
    # Sort by score and select top sentences
    top_indices = sorted([idx for idx, score in sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:max_sentences]])
    
    # Reconstruct the summary
    summary = ' '.join([sentences[idx] for idx in top_indices])
    
    return summary


@handle_errors
def categorize_information(texts: List[str], categories: List[str]) -> Dict[str, List[str]]:
    """
    Categorize information into predefined categories.
    
    Args:
        texts: List of text snippets
        categories: List of categories to use
        
    Returns:
        Dictionary mapping categories to relevant text snippets
    """
    result = defaultdict(list)
    
    for text in texts:
        max_score = 0
        best_category = "uncategorized"
        
        for category in categories:
            # Simple scoring based on word frequency
            category_words = category.lower().split()
            score = 0
            
            for word in category_words:
                # Count occurrences of the category word in the text
                # Using word boundaries to match whole words
                matches = len(re.findall(r'\b' + re.escape(word) + r'\b', text.lower()))
                score += matches
            
            if score > max_score:
                max_score = score
                best_category = category
        
        # Add to the appropriate category
        result[best_category].append(text)
    
    # Ensure all categories are present in the result
    for category in categories:
        if category not in result:
            result[category] = []
    
    return dict(result)


@handle_errors
def extract_market_data(text: str) -> Dict[str, Any]:
    """
    Extract market-related data from text.
    
    Args:
        text: Text containing market information
        
    Returns:
        Dictionary with extracted market data
    """
    data = {
        "market_size": None,
        "growth_rate": None,
        "competitors": [],
        "trends": []
    }
    
    # Extract market size (looking for dollar amounts with billion/million)
    market_size_pattern = r'\$\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion)'
    market_size_matches = re.findall(market_size_pattern, text, re.IGNORECASE)
    if market_size_matches:
        value, unit = market_size_matches[0]
        data["market_size"] = f"${value} {unit}"
    
    # Extract growth rate (looking for percentage patterns)
    growth_pattern = r'(\d+(?:\.\d+)?)%\s*(?:annual|annually|year|growth|CAGR)'
    growth_matches = re.findall(growth_pattern, text, re.IGNORECASE)
    if growth_matches:
        data["growth_rate"] = f"{growth_matches[0]}%"
    
    # Extract potential competitors
    # This is simplistic and would need refinement for real use
    competitor_patterns = [
        r'competitors include(.*?)(?:\.|\n)',
        r'competing (?:companies|products) (?:include|are)(.*?)(?:\.|\n)',
        r'competitive landscape includes(.*?)(?:\.|\n)'
    ]
    
    for pattern in competitor_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Extract company names (assuming they're separated by commas)
            companies = re.findall(r'([A-Z][A-Za-z0-9\s]+?)(?:,|\sand\s|\.|\n)', matches[0])
            data["competitors"].extend([company.strip() for company in companies])
    
    # Extract trends
    trend_patterns = [
        r'trends include(.*?)(?:\.|\n)',
        r'trending towards(.*?)(?:\.|\n)',
        r'recent trends(.*?)(?:\.|\n)'
    ]
    
    for pattern in trend_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Extract trend descriptions
            trends = re.split(r',|\sand\s', matches[0])
            data["trends"].extend([trend.strip() for trend in trends if trend.strip()])
    
    return data