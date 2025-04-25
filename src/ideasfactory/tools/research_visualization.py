"""
Research visualization tool for IdeasFactory agents.

This module provides visualization capabilities for research data without
imposing specific visualization patterns, allowing agents to create
their own visualizations based on their analysis.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import re
from collections import defaultdict

from ideasfactory.utils.error_handler import handle_errors

# Configure logging
logger = logging.getLogger(__name__)


@handle_errors
def create_ascii_table(
    headers: List[str],
    rows: List[List[str]],
    max_width: int = 120
) -> str:
    """
    Create a simple ASCII table for displaying tabular data.
    
    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of cell values)
        max_width: Maximum width for columns
        
    Returns:
        Formatted ASCII table
    """
    if not headers or not rows:
        return "No data to display"
    
    # Convert all values to strings
    str_rows = [[str(cell) for cell in row] for row in rows]
    
    # Calculate column widths (minimum width is the header length)
    col_widths = [len(header) for header in headers]
    
    # Update column widths based on data
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], min(len(cell), max_width))
    
    # Create the table
    table = []
    
    # Add header row
    header_row = "│ " + " │ ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers)) + " │"
    table.append("┌" + "─" * (len(header_row) - 2) + "┐")
    table.append(header_row)
    table.append("├" + "─" * (len(header_row) - 2) + "┤")
    
    # Add data rows
    for row in str_rows:
        # Ensure row has the same number of columns as headers
        padded_row = row + [""] * (len(headers) - len(row))
        data_row = "│ " + " │ ".join(cell.ljust(col_widths[i]) if len(cell) <= max_width 
                                     else cell[:max_width-3] + "..." 
                                     for i, cell in enumerate(padded_row[:len(headers)])) + " │"
        table.append(data_row)
    
    table.append("└" + "─" * (len(header_row) - 2) + "┘")
    
    return "\n".join(table)


@handle_errors
def create_ascii_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    max_width: int = 50,
    sort: bool = False
) -> str:
    """
    Create a simple ASCII bar chart for visualization.
    
    Args:
        labels: List of category labels
        values: List of values corresponding to labels
        title: Chart title
        max_width: Maximum width for the bars
        sort: Whether to sort bars by value (descending)
        
    Returns:
        Formatted ASCII bar chart
    """
    if not labels or not values or len(labels) != len(values):
        return "Invalid data for bar chart"
    
    # Sort data if requested
    if sort:
        # Sort by values (descending)
        sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_data)
    
    # Find the maximum value for scaling
    max_value = max(values) if values else 0
    
    # Create the chart
    chart = []
    
    # Add title if provided
    if title:
        chart.append(title)
        chart.append("=" * len(title))
        chart.append("")
    
    # Find the maximum label length for alignment
    max_label_len = max(len(label) for label in labels) if labels else 0
    
    # Create the bars
    for i, (label, value) in enumerate(zip(labels, values)):
        # Calculate bar length
        if max_value > 0:
            bar_length = int((value / max_value) * max_width)
        else:
            bar_length = 0
        
        # Format the value
        if isinstance(value, int):
            value_str = str(value)
        else:
            value_str = f"{value:.2f}"
        
        # Create the bar
        bar = "█" * bar_length
        
        # Add to chart
        chart.append(f"{label.ljust(max_label_len)} │ {bar} {value_str}")
    
    return "\n".join(chart)


@handle_errors
def create_ascii_histogram(
    values: List[float],
    bins: int = 10,
    title: str = "",
    max_width: int = 50
) -> str:
    """
    Create a simple ASCII histogram for numerical data.
    
    Args:
        values: List of numerical values
        bins: Number of bins
        title: Chart title
        max_width: Maximum width for the bars
        
    Returns:
        Formatted ASCII histogram
    """
    if not values:
        return "No data for histogram"
    
    # Calculate the bin edges
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        # All values are the same
        return f"All values are {min_val}"
    
    bin_width = (max_val - min_val) / bins
    bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
    
    # Count values in each bin
    bin_counts = [0] * bins
    
    for value in values:
        # Find the bin index for this value
        bin_idx = 0
        while bin_idx < bins - 1 and value > bin_edges[bin_idx + 1]:
            bin_idx += 1
        bin_counts[bin_idx] += 1
    
    # Create the histogram
    histogram = []
    
    # Add title if provided
    if title:
        histogram.append(title)
        histogram.append("=" * len(title))
        histogram.append("")
    
    # Find the maximum count for scaling
    max_count = max(bin_counts) if bin_counts else 0
    
    # Create the bars
    for i in range(bins):
        # Format the bin range
        if i == bins - 1:
            # Last bin includes the upper edge
            bin_range = f"[{bin_edges[i]:.2f}, {bin_edges[i+1]:.2f}]"
        else:
            bin_range = f"[{bin_edges[i]:.2f}, {bin_edges[i+1]:.2f})"
        
        # Calculate bar length
        if max_count > 0:
            bar_length = int((bin_counts[i] / max_count) * max_width)
        else:
            bar_length = 0
        
        # Create the bar
        bar = "█" * bar_length
        
        # Add to histogram
        histogram.append(f"{bin_range.ljust(20)} │ {bar} {bin_counts[i]}")
    
    return "\n".join(histogram)


@handle_errors
def create_tree_visualization(
    tree_data: Dict[str, Any],
    indent: str = "  "
) -> str:
    """
    Create a textual tree visualization for hierarchical data.
    
    Args:
        tree_data: Hierarchical data in dictionary format
        indent: Indentation string for each level
        
    Returns:
        Formatted tree visualization
    """
    def _build_tree(node, level=0, prefix="", is_last=True, result=None):
        if result is None:
            result = []
        
        # Determine the current node's branch display
        if level > 0:
            branch = prefix + ("└─ " if is_last else "├─ ")
        else:
            branch = ""
        
        # Handle various node types
        if isinstance(node, dict):
            if level == 0:
                # Root node
                node_items = list(node.items())
                if len(node_items) == 1 and isinstance(node_items[0][1], dict):
                    # If the root has a single child that's a dict, treat it as the root
                    key, child = node_items[0]
                    result.append(key)
                    new_prefix = prefix + indent
                    _build_tree(child, level + 1, new_prefix, True, result)
                else:
                    # Process all items at the root level
                    for i, (key, child) in enumerate(node_items):
                        is_last_item = i == len(node_items) - 1
                        if isinstance(child, dict) or isinstance(child, list):
                            # If child is a complex type, show key and then recurse
                            result.append(branch + str(key))
                            new_prefix = prefix + (indent if is_last else "│ " + indent[1:])
                            _build_tree(child, level + 1, new_prefix, is_last_item, result)
                        else:
                            # For simple values, show key: value
                            result.append(branch + f"{key}: {child}")
                        
            else:
                # Non-root dict
                items = list(node.items())
                for i, (key, child) in enumerate(items):
                    is_last_item = i == len(items) - 1
                    if isinstance(child, dict) or isinstance(child, list):
                        # If child is a complex type, show key and then recurse
                        result.append(branch + str(key))
                        new_prefix = prefix + (indent if is_last else "│ " + indent[1:])
                        _build_tree(child, level + 1, new_prefix, is_last_item, result)
                    else:
                        # For simple values, show key: value
                        result.append(branch + f"{key}: {child}")
        
        elif isinstance(node, list):
            # Process list items
            for i, item in enumerate(node):
                is_last_item = i == len(node) - 1
                if isinstance(item, dict) or isinstance(item, list):
                    # If item is a complex type, show the index and then recurse
                    result.append(branch + f"[{i}]")
                    new_prefix = prefix + (indent if is_last else "│ " + indent[1:])
                    _build_tree(item, level + 1, new_prefix, is_last_item, result)
                else:
                    # For simple values, show the index: value
                    result.append(branch + f"[{i}]: {item}")
        
        else:
            # Simple value, just show it
            result.append(branch + str(node))
        
        return result
    
    # Build the tree
    tree_lines = _build_tree(tree_data)
    
    return "\n".join(tree_lines)


@handle_errors
def create_text_heatmap(
    data: List[List[float]],
    row_labels: List[str] = None,
    col_labels: List[str] = None,
    title: str = "",
    gradient: List[str] = None
) -> str:
    """
    Create a text-based heatmap for visualizing matrix data.
    
    Args:
        data: 2D matrix of values
        row_labels: Labels for rows
        col_labels: Labels for columns
        title: Heatmap title
        gradient: List of characters to use for gradient (default = space to full block)
        
    Returns:
        Formatted text heatmap
    """
    if not data:
        return "No data for heatmap"
    
    # Check data dimensions
    num_rows = len(data)
    num_cols = max(len(row) for row in data) if data else 0
    
    # Default gradient characters (from space to full block)
    if gradient is None:
        gradient = [" ", "░", "▒", "▓", "█"]
    
    # Create default labels if not provided
    if row_labels is None:
        row_labels = [f"Row {i+1}" for i in range(num_rows)]
    
    if col_labels is None:
        col_labels = [f"Col {i+1}" for i in range(num_cols)]
    
    # Ensure labels are strings
    row_labels = [str(label) for label in row_labels]
    col_labels = [str(label) for label in col_labels]
    
    # Find min and max values for scaling
    flat_data = [value for row in data for value in row]
    min_val = min(flat_data) if flat_data else 0
    max_val = max(flat_data) if flat_data else 1
    
    # Handle case where all values are the same
    if min_val == max_val:
        value_range = 1
    else:
        value_range = max_val - min_val
    
    # Find the max row label length for alignment
    max_row_label_len = max(len(label) for label in row_labels) if row_labels else 0
    
    # Create the heatmap
    heatmap = []
    
    # Add title if provided
    if title:
        heatmap.append(title)
        heatmap.append("=" * len(title))
        heatmap.append("")
    
    # Add column headers
    header = " " * max_row_label_len + " │"
    for col_label in col_labels[:num_cols]:
        # Truncate long labels
        if len(col_label) > 5:
            col_label = col_label[:4] + "…"
        header += " " + col_label.center(5)
    
    heatmap.append(header)
    heatmap.append("─" * max_row_label_len + "─┼" + "─" * (6 * num_cols + 1))
    
    # Add data rows
    for i, row in enumerate(data):
        # Ensure the row has the correct number of columns
        padded_row = row + [0] * (num_cols - len(row))
        
        # Get the row label
        row_label = row_labels[i] if i < len(row_labels) else f"Row {i+1}"
        
        # Create the row string
        row_str = row_label.ljust(max_row_label_len) + " │"
        
        for value in padded_row[:num_cols]:
            # Normalize the value and select a gradient character
            if value_range > 0:
                normalized = (value - min_val) / value_range
            else:
                normalized = 0.5
            
            # Map to gradient character
            grad_idx = min(int(normalized * (len(gradient) - 1)), len(gradient) - 1)
            grad_char = gradient[grad_idx]
            
            # Format the value
            if isinstance(value, int):
                value_str = str(value)
            else:
                value_str = f"{value:.2f}"
            
            # Truncate if too long
            if len(value_str) > 5:
                value_str = value_str[:5]
            
            # Add to row
            row_str += " " + grad_char * 2 + value_str.rjust(3)
        
        heatmap.append(row_str)
    
    return "\n".join(heatmap)


@handle_errors
def create_network_visualization(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    title: str = ""
) -> str:
    """
    Create a text-based visualization of a network/graph.
    
    Args:
        nodes: List of node dictionaries with at least 'id' and 'label' fields
        edges: List of edge dictionaries with 'source' and 'target' fields
        title: Visualization title
        
    Returns:
        Formatted text network visualization
    """
    if not nodes:
        return "No nodes to visualize"
    
    # Create a visualization
    visualization = []
    
    # Add title if provided
    if title:
        visualization.append(title)
        visualization.append("=" * len(title))
        visualization.append("")
    
    # Create a mapping from node IDs to indices
    node_map = {node['id']: i for i, node in enumerate(nodes)}
    
    # Build an adjacency list
    adjacency = defaultdict(list)
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        
        if source in node_map and target in node_map:
            # Get the source and target indices
            source_idx = node_map[source]
            target_idx = node_map[target]
            
            # Add the edge to the adjacency list
            adjacency[source_idx].append(target_idx)
    
    # List all nodes
    visualization.append("Nodes:")
    visualization.append("-----")
    for i, node in enumerate(nodes):
        label = node.get('label', node.get('id', f"Node {i}"))
        node_info = f"{i+1}. {label}"
        
        # Add any additional attributes
        attrs = []
        for key, value in node.items():
            if key not in ['id', 'label']:
                attrs.append(f"{key}: {value}")
        
        if attrs:
            node_info += " (" + ", ".join(attrs) + ")"
        
        visualization.append(node_info)
    
    visualization.append("")
    
    # List all connections
    visualization.append("Connections:")
    visualization.append("-----------")
    
    for source_idx in sorted(adjacency.keys()):
        source_label = nodes[source_idx].get('label', nodes[source_idx].get('id', f"Node {source_idx}"))
        
        for target_idx in sorted(adjacency[source_idx]):
            target_label = nodes[target_idx].get('label', nodes[target_idx].get('id', f"Node {target_idx}"))
            
            # Find the edge data
            edge_data = []
            for edge in edges:
                if (edge.get('source') == nodes[source_idx].get('id') and 
                    edge.get('target') == nodes[target_idx].get('id')):
                    # Add any attributes except source and target
                    for key, value in edge.items():
                        if key not in ['source', 'target']:
                            edge_data.append(f"{key}: {value}")
                    break
            
            connection = f"{source_label} → {target_label}"
            if edge_data:
                connection += " (" + ", ".join(edge_data) + ")"
            
            visualization.append(connection)
    
    # If there are no connections, say so
    if not adjacency:
        visualization.append("No connections between nodes")
    
    return "\n".join(visualization)


@handle_errors
def create_text_scatter_plot(
    x_values: List[float],
    y_values: List[float],
    labels: List[str] = None,
    title: str = "",
    width: int = 60,
    height: int = 20
) -> str:
    """
    Create a text-based scatter plot.
    
    Args:
        x_values: List of x-coordinates
        y_values: List of y-coordinates
        labels: Optional labels for points
        title: Plot title
        width: Plot width
        height: Plot height
        
    Returns:
        Formatted text scatter plot
    """
    if not x_values or not y_values or len(x_values) != len(y_values):
        return "Invalid data for scatter plot"
    
    # Create a 2D grid for the plot
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Find min and max values for scaling
    x_min = min(x_values)
    x_max = max(x_values)
    y_min = min(y_values)
    y_max = max(y_values)
    
    # Ensure we don't have zero ranges
    x_range = max(0.001, x_max - x_min)
    y_range = max(0.001, y_max - y_min)
    
    # Place points on the grid
    point_positions = {}  # Maps grid positions to point indices
    
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        # Scale to grid coordinates
        grid_x = int((x - x_min) / x_range * (width - 1))
        grid_y = height - 1 - int((y - y_min) / y_range * (height - 1))
        
        # Ensure coordinates are within bounds
        grid_x = max(0, min(width - 1, grid_x))
        grid_y = max(0, min(height - 1, grid_y))
        
        # Place point on grid
        grid[grid_y][grid_x] = '●'
        
        # Save position for label reference
        point_positions[(grid_x, grid_y)] = i
    
    # Create the scatter plot
    scatter_plot = []
    
    # Add title if provided
    if title:
        scatter_plot.append(title)
        scatter_plot.append("=" * len(title))
        scatter_plot.append("")
    
    # Y-axis scale
    y_scale = [y_min + (y_range * i / (height - 1)) for i in range(height)]
    y_scale.reverse()  # Reverse to match grid orientation
    
    # Add grid with axes
    for i, row in enumerate(grid):
        # Add y-axis scale
        if i % (height // 5) == 0 or i == height - 1:
            y_val = y_scale[i]
            if isinstance(y_val, int):
                y_label = f"{y_val:3d} "
            else:
                y_label = f"{y_val:3.1f} "
        else:
            y_label = "    "
        
        scatter_plot.append(y_label + ''.join(row))
    
    # Add x-axis scale
    x_axis = "    " + "".join(["|" if i % (width // 5) == 0 else " " for i in range(width)])
    scatter_plot.append(x_axis)
    
    x_scale = "    "
    for i in range(0, width, width // 5):
        x_val = x_min + (x_range * i / (width - 1))
        if isinstance(x_val, int):
            x_label = str(x_val)
        else:
            x_label = f"{x_val:.1f}"
        
        # Pad or truncate to fit position
        if len(x_label) > width // 5:
            x_label = x_label[:width // 5]
        else:
            x_label = x_label.ljust(width // 5)
        
        x_scale += x_label
    
    scatter_plot.append(x_scale)
    
    # Add point labels if provided
    if labels:
        scatter_plot.append("")
        scatter_plot.append("Points:")
        
        for (grid_x, grid_y), idx in sorted(point_positions.items()):
            if idx < len(labels):
                x_val = x_values[idx]
                y_val = y_values[idx]
                label = labels[idx]
                
                if isinstance(x_val, int):
                    x_str = str(x_val)
                else:
                    x_str = f"{x_val:.2f}"
                
                if isinstance(y_val, int):
                    y_str = str(y_val)
                else:
                    y_str = f"{y_val:.2f}"
                
                scatter_plot.append(f"- ({x_str}, {y_str}): {label}")
    
    return "\n".join(scatter_plot)


@handle_errors
def create_venn_diagram(
    sets: Dict[str, List[Any]],
    title: str = ""
) -> str:
    """
    Create a text-based Venn diagram visualization.
    
    Args:
        sets: Dictionary mapping set names to their elements
        title: Diagram title
        
    Returns:
        Formatted text Venn diagram
    """
    if not sets:
        return "No sets to visualize"
    
    # Calculate set intersections and differences
    set_names = list(sets.keys())
    set_elements = {name: set(elements) for name, elements in sets.items()}
    
    # Create the visualization
    diagram = []
    
    # Add title if provided
    if title:
        diagram.append(title)
        diagram.append("=" * len(title))
        diagram.append("")
    
    # Describe each set
    diagram.append("Sets:")
    for name, elements in sorted(sets.items()):
        diagram.append(f"- {name}: {len(elements)} elements")
    
    diagram.append("")
    
    # Show set relationships
    if len(set_names) == 1:
        # Single set
        name = set_names[0]
        elements = set_elements[name]
        
        diagram.append(f"Set: {name}")
        diagram.append("┌" + "─" * (len(name) + 2) + "┐")
        diagram.append(f"│ {name} │")
        diagram.append("└" + "─" * (len(name) + 2) + "┘")
        diagram.append(f"Elements: {len(elements)}")
        
    elif len(set_names) == 2:
        # Two sets - show intersection and differences
        name1, name2 = set_names
        set1, set2 = set_elements[name1], set_elements[name2]
        
        intersection = set1 & set2
        only_set1 = set1 - set2
        only_set2 = set2 - set1
        
        # ASCII art for two-set Venn diagram
        diagram.append("Two-Set Relationship:")
        diagram.append("   ┌─────────┐     ┌─────────┐")
        diagram.append(f"   │  {name1.ljust(7)} │     │  {name2.ljust(7)} │")
        diagram.append("   │         │     │         │")
        diagram.append("   │    A    ├─────┤    B    │")
        diagram.append("   │         │  C  │         │")
        diagram.append("   │         │     │         │")
        diagram.append("   └─────────┘     └─────────┘")
        diagram.append("")
        diagram.append(f"A: Only in {name1}: {len(only_set1)} elements")
        diagram.append(f"B: Only in {name2}: {len(only_set2)} elements")
        diagram.append(f"C: In both sets: {len(intersection)} elements")
        
    elif len(set_names) == 3:
        # Three sets - show all intersections
        name1, name2, name3 = set_names
        set1, set2, set3 = set_elements[name1], set_elements[name2], set_elements[name3]
        
        # Calculate all possible regions
        only_set1 = set1 - set2 - set3
        only_set2 = set2 - set1 - set3
        only_set3 = set3 - set1 - set2
        set1_set2 = set1 & set2 - set3
        set1_set3 = set1 & set3 - set2
        set2_set3 = set2 & set3 - set1
        all_sets = set1 & set2 & set3
        
        # ASCII art for three-set Venn diagram
        diagram.append("Three-Set Relationship:")
        diagram.append("        ┌─────────┐")
        diagram.append(f"        │  {name1.ljust(7)} │")
        diagram.append("        │    A    │")
        diagram.append("    ┌───┼───┐     │")
        diagram.append(f"    │   │ D │     │   ┌───────┐")
        diagram.append(f"    │{name2.ljust(3)}│   │     │   │{name3.ljust(7)}│")
        diagram.append("    │ B │ G │  E  │   │   C   │")
        diagram.append("    │   │   │     │   │       │")
        diagram.append("    └───┼───┘     │   │       │")
        diagram.append("        │     F   ├───┤       │")
        diagram.append("        │         │   │       │")
        diagram.append("        └─────────┘   └───────┘")
        diagram.append("")
        diagram.append(f"A: Only in {name1}: {len(only_set1)} elements")
        diagram.append(f"B: Only in {name2}: {len(only_set2)} elements") 
        diagram.append(f"C: Only in {name3}: {len(only_set3)} elements")
        diagram.append(f"D: In {name1} and {name2} only: {len(set1_set2)} elements")
        diagram.append(f"E: In {name1} and {name3} only: {len(set1_set3)} elements")
        diagram.append(f"F: In {name2} and {name3} only: {len(set2_set3)} elements")
        diagram.append(f"G: In all three sets: {len(all_sets)} elements")
        
    else:
        # More than three sets - show a matrix of intersections
        diagram.append("Set Intersections:")
        
        # Create a table for set intersections
        headers = [""] + set_names
        rows = []
        
        for i, name1 in enumerate(set_names):
            row = [name1]
            for j, name2 in enumerate(set_names):
                if i == j:
                    # Diagonal - show set size
                    row.append(str(len(set_elements[name1])))
                else:
                    # Off-diagonal - show intersection size
                    intersection = set_elements[name1] & set_elements[name2]
                    row.append(str(len(intersection)))
            
            rows.append(row)
        
        # Add the intersection table
        diagram.append(create_ascii_table(headers, rows))
    
    return "\n".join(diagram)


@handle_errors
def create_word_cloud(
    word_frequencies: Dict[str, int],
    max_words: int = 25,
    max_size: int = 5
) -> str:
    """
    Create a simple text-based word cloud.
    
    Args:
        word_frequencies: Dictionary mapping words to their frequencies
        max_words: Maximum number of words to include
        max_size: Maximum size factor for words
        
    Returns:
        Formatted text word cloud
    """
    if not word_frequencies:
        return "No words to visualize"
    
    # Sort words by frequency
    sorted_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
    
    # Limit to max_words
    top_words = sorted_words[:max_words]
    
    # Find the maximum frequency
    max_freq = top_words[0][1] if top_words else 0
    
    # Create the word cloud
    cloud = []
    
    for word, freq in top_words:
        # Scale the size
        if max_freq > 0:
            size = 1 + int((freq / max_freq) * (max_size - 1))
        else:
            size = 1
        
        # Adjust word size by repeating characters
        sized_word = ""
        for char in word:
            sized_word += char * size
        
        cloud.append(sized_word)
    
    # Shuffle the order for a more cloud-like appearance
    import random
    random.shuffle(cloud)
    
    # Group words into lines
    lines = []
    current_line = ""
    max_line_length = 60
    
    for word in cloud:
        if len(current_line) + len(word) + 1 <= max_line_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)


@handle_errors
def create_timeline(
    events: List[Dict[str, Any]],
    title: str = ""
) -> str:
    """
    Create a text-based timeline visualization.
    
    Args:
        events: List of event dictionaries with 'time' and 'description' fields
        title: Timeline title
        
    Returns:
        Formatted text timeline
    """
    if not events:
        return "No events to visualize"
    
    # Sort events by time
    sorted_events = sorted(events, key=lambda x: x.get('time', ''))
    
    # Create the timeline
    timeline = []
    
    # Add title if provided
    if title:
        timeline.append(title)
        timeline.append("=" * len(title))
        timeline.append("")
    
    # Add events
    for i, event in enumerate(sorted_events):
        time = event.get('time', '')
        description = event.get('description', '')
        
        # Create the timeline entry
        if i == 0:
            # First event
            entry = f"● {time} - {description}"
        else:
            # Add a connector from the previous event
            entry = "│\n"
            entry += f"● {time} - {description}"
        
        timeline.append(entry)
    
    return "\n".join(timeline)


@handle_errors
def generate_mind_map(
    central_topic: str,
    topics: Dict[str, List[str]],
    max_width: int = 100
) -> str:
    """
    Generate a simple text-based mind map.
    
    Args:
        central_topic: The central topic of the mind map
        topics: Dictionary mapping main topics to their subtopics
        max_width: Maximum width for the mind map
        
    Returns:
        Formatted text mind map
    """
    if not central_topic or not topics:
        return "Insufficient data for mind map"
    
    # Create the mind map
    mind_map = []
    
    # Add central topic
    pad = " " * ((max_width - len(central_topic)) // 2)
    mind_map.append(pad + central_topic)
    
    # Main branch connector
    branch_count = len(topics)
    if branch_count > 0:
        connector_width = min(max_width - 2, branch_count * 8)
        connector = " " * ((max_width - connector_width) // 2) + "┬" + "─" * (connector_width - 2) + "┬"
        mind_map.append(connector)
    
    # Calculate positions for main topic branches
    positions = []
    if branch_count > 0:
        step = connector_width / branch_count
        for i in range(branch_count):
            positions.append(int((max_width - connector_width) / 2 + i * step))
    
    # Add main topics and their subtopics
    max_subtopics = 0
    main_topics = list(topics.keys())
    
    # First, add main topics with vertical connectors
    main_topic_line = " " * max_width
    for i, topic in enumerate(main_topics):
        pos = positions[i]
        main_topic_line = main_topic_line[:pos] + "│" + main_topic_line[pos+1:]
    mind_map.append(main_topic_line)
    
    # Then, add each main topic with its subtopics
    for i, topic in enumerate(main_topics):
        pos = positions[i]
        
        # Main topic
        indent = " " * pos
        topic_line = indent + "┌" + "─" * (len(topic) + 2) + "┐"
        mind_map.append(topic_line)
        
        topic_text = indent + "│ " + topic + " │"
        mind_map.append(topic_text)
        
        topic_bottom = indent + "└" + "─" * (len(topic) + 2) + "┘"
        mind_map.append(topic_bottom)
        
        # Subtopics
        subtopics = topics[topic]
        if subtopics:
            # Vertical connector
            mind_map.append(indent + "│")
            
            # Add each subtopic
            for j, subtopic in enumerate(subtopics):
                if j < len(subtopics) - 1:
                    # Not the last subtopic
                    mind_map.append(indent + "├── " + subtopic)
                    mind_map.append(indent + "│")
                else:
                    # Last subtopic
                    mind_map.append(indent + "└── " + subtopic)
            
            max_subtopics = max(max_subtopics, len(subtopics))
    
    return "\n".join(mind_map)