"""
Enhanced data analysis tool for IdeasFactory agents.

This module provides data analysis capabilities without imposing analysis
patterns or filtering results, giving research agents the freedom to develop
their own analysis strategies.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Set, Tuple
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import pandas as pd
import numpy as np
from scipy import stats
import math
import itertools

from ideasfactory.utils.error_handler import handle_errors

# Configure logging
logger = logging.getLogger(__name__)


@handle_errors
def extract_text_features(text: str) -> Dict[str, Any]:
    """
    Extract basic statistical and linguistic features from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with extracted features
    """
    # Basic text statistics
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.split(r'[.!?]+', text))
    
    # Word frequency analysis
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    common_words = word_freq.most_common(20)
    
    # Readability metrics
    if sentence_count > 0:
        avg_words_per_sentence = word_count / sentence_count
    else:
        avg_words_per_sentence = 0
        
    if word_count > 0:
        avg_word_length = sum(len(word) for word in words) / word_count
    else:
        avg_word_length = 0
    
    # Extract potential entities
    potential_entities = []
    for match in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text):
        potential_entities.append(match.group())
    
    return {
        "word_count": word_count,
        "character_count": char_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_word_length": avg_word_length,
        "common_words": common_words,
        "potential_entities": list(set(potential_entities))
    }


@handle_errors
def extract_patterns(texts: List[str], pattern: str) -> List[Dict[str, Any]]:
    """
    Extract text matching a specific regex pattern from a list of texts.
    
    Args:
        texts: List of text strings to search
        pattern: Regular expression pattern to match
        
    Returns:
        List of dictionaries with matched text and source index
    """
    matches = []
    
    for i, text in enumerate(texts):
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            matches.append({
                "text": match.group(),
                "source_index": i,
                "start": match.start(),
                "end": match.end()
            })
    
    return matches


@handle_errors
def find_similar_texts(
    target_text: str, 
    candidate_texts: List[str], 
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Find texts similar to a target text using sequence matching.
    
    Args:
        target_text: Target text to compare against
        candidate_texts: List of candidate texts to check for similarity
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        List of similar texts with similarity scores
    """
    similar_texts = []
    
    for i, candidate in enumerate(candidate_texts):
        similarity = SequenceMatcher(None, target_text.lower(), candidate.lower()).ratio()
        
        if similarity >= threshold:
            similar_texts.append({
                "text": candidate,
                "similarity": similarity,
                "index": i
            })
    
    # Sort by similarity (highest first)
    similar_texts.sort(key=lambda x: x["similarity"], reverse=True)
    
    return similar_texts


@handle_errors
def cluster_texts(
    texts: List[str], 
    max_clusters: int = 5,
    min_similarity: float = 0.3
) -> Dict[str, Any]:
    """
    Cluster texts based on similarity.
    
    Args:
        texts: List of texts to cluster
        max_clusters: Maximum number of clusters to create
        min_similarity: Minimum similarity to consider texts related
        
    Returns:
        Dictionary with clustering results
    """
    if not texts:
        return {"clusters": [], "labels": []}
    
    # Calculate similarity matrix
    n = len(texts)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                similarity = SequenceMatcher(None, texts[i].lower(), texts[j].lower()).ratio()
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity
    
    # Simple clustering algorithm
    remaining = set(range(n))
    clusters = []
    cluster_labels = [-1] * n  # -1 means unclustered
    
    while remaining and len(clusters) < max_clusters:
        # Find the element with highest average similarity to others
        best_idx = max(remaining, key=lambda idx: np.mean([
            similarity_matrix[idx, j] for j in remaining if j != idx
        ]))
        
        # Create a new cluster with this element
        current_cluster = [best_idx]
        cluster_labels[best_idx] = len(clusters)
        remaining.remove(best_idx)
        
        # Find elements similar to this one
        for idx in list(remaining):
            if similarity_matrix[best_idx, idx] >= min_similarity:
                current_cluster.append(idx)
                cluster_labels[idx] = len(clusters)
                remaining.remove(idx)
        
        clusters.append(current_cluster)
    
    # Add remaining items to the closest cluster or create a new one
    if remaining:
        # If we haven't reached max clusters, create a new one
        if len(clusters) < max_clusters:
            new_cluster = list(remaining)
            for idx in new_cluster:
                cluster_labels[idx] = len(clusters)
            clusters.append(new_cluster)
        else:
            # Add each remaining item to its closest cluster
            for idx in remaining:
                # Find closest cluster
                closest_cluster = max(range(len(clusters)), 
                                     key=lambda c: np.mean([similarity_matrix[idx, j] for j in clusters[c]]))
                clusters[closest_cluster].append(idx)
                cluster_labels[idx] = closest_cluster
    
    # Format clusters with texts
    formatted_clusters = []
    for cluster_idx, indices in enumerate(clusters):
        cluster_texts = [texts[idx] for idx in indices]
        
        # Find representative text (closest to cluster centroid)
        if len(cluster_texts) > 1:
            # Representative is the one with highest average similarity to others
            avg_similarities = []
            for i, idx in enumerate(indices):
                avg_sim = np.mean([similarity_matrix[idx, j] for j in indices if j != idx])
                avg_similarities.append(avg_sim)
            
            representative_idx = indices[np.argmax(avg_similarities)]
            representative = texts[representative_idx]
        else:
            representative = cluster_texts[0]
        
        formatted_clusters.append({
            "id": cluster_idx,
            "size": len(cluster_texts),
            "texts": cluster_texts,
            "representative": representative,
            "indices": indices
        })
    
    return {
        "clusters": formatted_clusters,
        "labels": cluster_labels,
        "similarity_matrix": similarity_matrix.tolist()
    }


@handle_errors
def extract_keywords(
    text: str, 
    max_keywords: int = 10,
    min_word_length: int = 3,
    exclude_words: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Extract important keywords from text.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to extract
        min_word_length: Minimum word length to consider
        exclude_words: List of words to exclude
        
    Returns:
        List of keywords with frequency information
    """
    if exclude_words is None:
        exclude_words = []
    
    # Common English stopwords
    stopwords = {
        "the", "and", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by", 
        "about", "is", "are", "was", "were", "be", "been", "being", "have", "has", 
        "had", "do", "does", "did", "but", "or", "as", "if", "when", "than", "because", 
        "while", "where", "how", "what", "who", "this", "that", "these", "those", "it", 
        "its", "it's", "from", "can", "could", "will", "would", "should", "not"
    }
    
    # Add custom exclude words
    stopwords.update(exclude_words)
    
    # Tokenize and clean text
    words = re.findall(r'\b[a-z]{%d,}\b' % min_word_length, text.lower())
    
    # Filter out stopwords
    words = [w for w in words if w not in stopwords]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Get most common words
    keywords = []
    for word, count in word_counts.most_common(max_keywords):
        # Calculate TF (Term Frequency)
        tf = count / len(words) if words else 0
        
        keywords.append({
            "word": word,
            "count": count,
            "tf": tf
        })
    
    return keywords


@handle_errors
def analyze_numeric_data(data: List[float]) -> Dict[str, Any]:
    """
    Perform statistical analysis on numeric data.
    
    Args:
        data: List of numeric values
        
    Returns:
        Dictionary with statistical analysis
    """
    if not data:
        return {"error": "No data provided"}
    
    analysis = {}
    
    # Basic statistics
    analysis["count"] = len(data)
    analysis["min"] = min(data)
    analysis["max"] = max(data)
    analysis["range"] = analysis["max"] - analysis["min"]
    analysis["sum"] = sum(data)
    analysis["mean"] = np.mean(data)
    analysis["median"] = np.median(data)
    analysis["variance"] = np.var(data) if len(data) > 1 else 0
    analysis["std_dev"] = np.std(data) if len(data) > 1 else 0
    
    # Calculate quartiles
    analysis["quartiles"] = {
        "q1": np.percentile(data, 25),
        "q2": np.percentile(data, 50),  # Same as median
        "q3": np.percentile(data, 75)
    }
    analysis["iqr"] = analysis["quartiles"]["q3"] - analysis["quartiles"]["q1"]
    
    # Calculate skewness and kurtosis if enough data
    if len(data) > 2:
        analysis["skewness"] = stats.skew(data)
        analysis["kurtosis"] = stats.kurtosis(data)
    
    # Determine distribution properties
    analysis["is_normal"] = False
    if len(data) >= 8:  # Need enough data for meaningful test
        _, p_value = stats.shapiro(data)
        analysis["normality_test"] = {
            "test": "Shapiro-Wilk",
            "p_value": p_value,
            "is_normal": p_value > 0.05
        }
        analysis["is_normal"] = p_value > 0.05
    
    return analysis


@handle_errors
def calculate_similarity_matrix(
    items: List[Any],
    attributes: List[str] = None,
    similarity_function: str = "jaccard"
) -> Dict[str, Any]:
    """
    Calculate similarity matrix between items based on their attributes.
    
    Args:
        items: List of dictionaries representing items
        attributes: List of attributes to consider for similarity
        similarity_function: Similarity function to use (jaccard, cosine, etc.)
        
    Returns:
        Dictionary with similarity matrix and related information
    """
    if not items:
        return {"matrix": [], "items": []}
    
    n = len(items)
    similarity_matrix = np.zeros((n, n))
    
    # If no attributes specified, use all common attributes
    if attributes is None:
        all_keys = set()
        for item in items:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        attributes = list(all_keys)
    
    # Calculate similarity between all pairs
    for i in range(n):
        for j in range(i, n):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                # Get attribute values for both items
                if similarity_function == "jaccard":
                    # For Jaccard, we need sets of attributes
                    set_i = set()
                    set_j = set()
                    
                    for attr in attributes:
                        if isinstance(items[i], dict) and attr in items[i]:
                            val_i = items[i][attr]
                            if isinstance(val_i, (list, set)):
                                set_i.update(val_i)
                            else:
                                set_i.add(val_i)
                        
                        if isinstance(items[j], dict) and attr in items[j]:
                            val_j = items[j][attr]
                            if isinstance(val_j, (list, set)):
                                set_j.update(val_j)
                            else:
                                set_j.add(val_j)
                    
                    # Calculate Jaccard similarity
                    if set_i or set_j:  # Avoid empty sets
                        similarity = len(set_i.intersection(set_j)) / len(set_i.union(set_j))
                    else:
                        similarity = 0.0
                
                elif similarity_function == "text":
                    # For text similarity, concatenate all text attributes
                    text_i = ""
                    text_j = ""
                    
                    for attr in attributes:
                        if isinstance(items[i], dict) and attr in items[i] and isinstance(items[i][attr], str):
                            text_i += " " + items[i][attr]
                        
                        if isinstance(items[j], dict) and attr in items[j] and isinstance(items[j][attr], str):
                            text_j += " " + items[j][attr]
                    
                    # Calculate text similarity using SequenceMatcher
                    similarity = SequenceMatcher(None, text_i.lower(), text_j.lower()).ratio()
                
                else:
                    # Default to simple equality count
                    matches = 0
                    total = 0
                    
                    for attr in attributes:
                        if (isinstance(items[i], dict) and attr in items[i] and 
                            isinstance(items[j], dict) and attr in items[j]):
                            total += 1
                            if items[i][attr] == items[j][attr]:
                                matches += 1
                    
                    similarity = matches / total if total > 0 else 0.0
                
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity
    
    # Format item labels for the result
    item_labels = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            # Try to find a good identifier attribute
            for attr in ["name", "title", "id"]:
                if attr in item:
                    item_labels.append(str(item[attr]))
                    break
            else:
                # No good identifier found, use index
                item_labels.append(f"Item {i}")
        else:
            # Not a dictionary, use string representation
            item_labels.append(str(item))
    
    return {
        "matrix": similarity_matrix.tolist(),
        "labels": item_labels,
        "attributes": attributes,
        "similarity_function": similarity_function
    }


@handle_errors
def find_correlations(
    data: Dict[str, List[float]],
    method: str = "pearson"
) -> Dict[str, Any]:
    """
    Find correlations between numeric variables.
    
    Args:
        data: Dictionary mapping variable names to lists of values
        method: Correlation method (pearson, spearman, kendall)
        
    Returns:
        Dictionary with correlation matrix and information
    """
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Calculate correlation matrix
    if method == "pearson":
        corr_matrix = df.corr(method='pearson')
    elif method == "spearman":
        corr_matrix = df.corr(method='spearman')
    elif method == "kendall":
        corr_matrix = df.corr(method='kendall')
    else:
        corr_matrix = df.corr(method='pearson')  # Default to Pearson
    
    # Find strongly correlated pairs
    strong_correlations = []
    variables = list(data.keys())
    
    for i, var1 in enumerate(variables):
        for j, var2 in enumerate(variables):
            if i < j:  # Only look at unique pairs
                correlation = corr_matrix.loc[var1, var2]
                
                # Add if correlation is strong (positive or negative)
                if abs(correlation) >= 0.5:
                    strong_correlations.append({
                        "variables": [var1, var2],
                        "correlation": correlation,
                        "strength": abs(correlation),
                        "direction": "positive" if correlation > 0 else "negative"
                    })
    
    # Sort by absolute correlation strength
    strong_correlations.sort(key=lambda x: x["strength"], reverse=True)
    
    return {
        "correlation_matrix": corr_matrix.to_dict(),
        "method": method,
        "variables": variables,
        "strong_correlations": strong_correlations
    }


@handle_errors
def analyze_categorical_data(
    data: List[Any],
    categories: List[str] = None
) -> Dict[str, Any]:
    """
    Analyze categorical data frequencies and distributions.
    
    Args:
        data: List of categorical values
        categories: Optional list of categories to analyze
        
    Returns:
        Dictionary with categorical analysis
    """
    if not data:
        return {"error": "No data provided"}
    
    # Count frequencies
    counter = Counter(data)
    
    # If categories provided, ensure all are represented
    if categories:
        for category in categories:
            if category not in counter:
                counter[category] = 0
    
    # Get total count
    total = sum(counter.values())
    
    # Calculate frequencies and percentages
    frequencies = []
    for category, count in counter.most_common():
        frequencies.append({
            "category": category,
            "count": count,
            "percentage": (count / total) * 100 if total > 0 else 0
        })
    
    # Information theory metrics
    entropy = 0
    if total > 0:
        for item in frequencies:
            p = item["count"] / total
            if p > 0:  # Avoid log(0)
                entropy -= p * math.log2(p)
    
    # Calculate diversity indexes
    diversity = {
        "count": len(counter),
        "entropy": entropy,
        "normalized_entropy": entropy / math.log2(len(counter)) if len(counter) > 0 else 0,
        "simpson_index": sum((count/total) ** 2 for count in counter.values()) if total > 0 else 0
    }
    
    # Calculate dominance (percentage of most common category)
    if frequencies:
        dominance = frequencies[0]["percentage"]
    else:
        dominance = 0
    
    return {
        "total": total,
        "frequencies": frequencies,
        "diversity": diversity,
        "dominance": dominance
    }


@handle_errors
def create_data_frame(
    data: Union[List[Dict[str, Any]], Dict[str, List[Any]]]
) -> Dict[str, Any]:
    """
    Create a data frame from input data with summary statistics.
    
    Args:
        data: Data in list-of-dicts or dict-of-lists format
        
    Returns:
        Dictionary with data frame information and summary
    """
    try:
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dicts format
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and all(isinstance(item, list) for item in data.values()):
            # Dict of lists format
            df = pd.DataFrame(data)
        else:
            return {"error": "Invalid data format. Provide either a list of dictionaries or a dictionary of lists."}
        
        # Basic info
        info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            numeric_summary = df[numeric_cols].describe().to_dict()
        else:
            numeric_summary = {}
        
        # Frequency counts for categorical columns (limit to top 5 values)
        categorical_cols = df.select_dtypes(exclude=['number']).columns
        categorical_summary = {}
        
        for col in categorical_cols:
            value_counts = df[col].value_counts().head(5).to_dict()
            categorical_summary[col] = [{"value": k, "count": v} for k, v in value_counts.items()]
        
        # Missing values
        missing_values = {col: int(df[col].isna().sum()) for col in df.columns}
        
        return {
            "info": info,
            "numeric_summary": numeric_summary,
            "categorical_summary": categorical_summary,
            "missing_values": missing_values
        }
    
    except Exception as e:
        logger.error(f"Error creating data frame: {str(e)}")
        return {"error": str(e)}


@handle_errors
def tokenize_and_count(
    text: str,
    min_length: int = 2,
    lowercase: bool = True,
    remove_stopwords: bool = True
) -> Dict[str, Any]:
    """
    Tokenize text and count tokens with various options.
    
    Args:
        text: Text to tokenize
        min_length: Minimum token length
        lowercase: Whether to convert to lowercase
        remove_stopwords: Whether to remove stopwords
        
    Returns:
        Dictionary with tokens and frequency information
    """
    # Process text
    if lowercase:
        text = text.lower()
    
    # Tokenize using regex to extract words
    tokens = re.findall(r'\b\w+\b', text)
    
    # Filter by length
    tokens = [token for token in tokens if len(token) >= min_length]
    
    # Remove stopwords if requested
    if remove_stopwords:
        stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 'which',
            'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such', 'both',
            'through', 'about', 'for', 'is', 'of', 'while', 'during', 'to', 'from', 'in',
            'on', 'at', 'by', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 's', 't', 'can', 'will', 'don', 'should', 'now'
        }
        
        tokens = [token for token in tokens if token not in stopwords]
    
    # Count tokens
    token_counts = Counter(tokens)
    
    # Prepare frequency information
    total_tokens = len(tokens)
    unique_tokens = len(token_counts)
    
    # Calculate lexical diversity
    if total_tokens > 0:
        lexical_diversity = unique_tokens / total_tokens
    else:
        lexical_diversity = 0
    
    # Prepare most common tokens
    most_common = [{"token": token, "count": count} for token, count in token_counts.most_common(20)]
    
    return {
        "total_tokens": total_tokens,
        "unique_tokens": unique_tokens,
        "lexical_diversity": lexical_diversity,
        "most_common": most_common,
        "all_counts": dict(token_counts)
    }