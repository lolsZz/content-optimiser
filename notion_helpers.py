"""
Notion-specific helper functions for Content Optimizer.

This module contains utilities for processing Notion.so exports, including
handling of Notion's content IDs, cleaning Notion-specific formatting,
and other Notion export specific optimizations.
"""

import re
import os
from pathlib import Path

# Pattern to match Notion IDs (32 hex characters, typically preceded by space or underscore)
NOTION_ID_PATTERN = re.compile(r'([^/\\]+?)[ _]([a-f0-9]{32})(?:\.[^/\\]*)?$')

# Pattern to remove Notion export artifacts
NOTION_EXPORT_ARTIFACTS = [
    # Notion export dividers (3+ dashes with optional spaces)
    (re.compile(r'^---+\s*$', re.MULTILINE), "\n"),
    
    # Notion export properties block
    (re.compile(r'^(?:Property|Properties):\s*\n(?:(?:[^\n]+: [^\n]+\n)+)', re.MULTILINE), ""),
    
    # Notion created/edited timestamps
    (re.compile(r'^(?:Created|Last Edited)(?:[ :]+).*?\d{4}\s*$', re.MULTILINE), ""),
    
    # Notion URL references
    (re.compile(r'https://www\.notion\.so/[a-f0-9]{32}'), ""),
    
    # Notion inline comments (double square brackets with text)
    (re.compile(r'\[\[([^\]]+)\]\]'), r'\1'),
    
    # Notion export citation markers
    (re.compile(r'\[(\d+)\]\(#cite-[a-f0-9-]+\)'), r'[\1]'),
]

# Table to convert Notion export metadata properties to markdown frontmatter
NOTION_PROPERTY_TO_FRONTMATTER = {
    "Title": "title",
    "Name": "title",
    "Tags": "tags",
    "Category": "category",
    "Categories": "categories",
    "Author": "author",
    "Authors": "authors",
    "Date": "date",
    "Published": "date",
    "Status": "status",
    "Description": "description",
    "Summary": "summary",
}

def extract_notion_id(path: str) -> tuple:
    """
    Extracts the Notion ID from a path element if present.
    
    Args:
        path: Path string possibly containing a Notion ID
        
    Returns:
        Tuple of (clean_name, notion_id) where notion_id is None if not found
    """
    match = NOTION_ID_PATTERN.search(path)
    if match:
        clean_name = match.group(1).strip()
        notion_id = match.group(2)
        return (clean_name, notion_id)
    
    # No ID found, return original path and None
    return (path, None)

def notion_clean_path(path: str) -> str:
    """
    Cleans a path by removing Notion IDs from each component.
    
    Args:
        path: Path string with possible Notion IDs
        
    Returns:
        Cleaned path string
    """
    path_parts = path.split('/')
    cleaned_parts = []
    
    for part in path_parts:
        clean_name, _ = extract_notion_id(part)
        cleaned_parts.append(clean_name)
    
    return '/'.join(cleaned_parts)

def clean_notion_content(content: str) -> str:
    """
    Cleans Notion-specific artifacts from the content.
    
    Args:
        content: String content from a Notion export
        
    Returns:
        Cleaned content string
    """
    if not content:
        return content
        
    # Process content with all defined artifact patterns
    result = content
    for pattern, replacement in NOTION_EXPORT_ARTIFACTS:
        result = pattern.sub(replacement, result)
        
    # Convert Notion properties to YAML frontmatter if properties block exists
    properties_match = re.search(r'^Properties:\s*\n((?:[^\n]+: [^\n]+\n)+)', result, re.MULTILINE)
    if properties_match:
        properties_block = properties_match.group(1)
        property_lines = properties_block.strip().split('\n')
        
        frontmatter_lines = ["---"]
        for line in property_lines:
            # Split property name and value
            if ': ' not in line:
                continue
                
            prop_name, prop_value = line.split(': ', 1)
            prop_name = prop_name.strip()
            prop_value = prop_value.strip()
            
            # Map to standard frontmatter names if possible
            fm_name = NOTION_PROPERTY_TO_FRONTMATTER.get(prop_name, prop_name.lower())
            
            # Format properly for YAML
            if prop_value.startswith('[') and prop_value.endswith(']'):
                # Handle list values (e.g., tags)
                values = [v.strip() for v in prop_value[1:-1].split(',')]
                frontmatter_lines.append(f"{fm_name}:")
                for value in values:
                    frontmatter_lines.append(f"  - {value}")
            else:
                # Handle scalar values
                frontmatter_lines.append(f"{fm_name}: {prop_value}")
        
        frontmatter_lines.append("---")
        frontmatter = "\n".join(frontmatter_lines)
        
        # Replace properties block with frontmatter
        result = re.sub(r'^Properties:\s*\n(?:[^\n]+: [^\n]+\n)+', frontmatter + "\n\n", result, flags=re.MULTILINE)
    
    return result.strip()

def build_notion_id_map(directory_path: str) -> dict:
    """
    Builds a map of clean paths to Notion IDs for all files and directories in 
    the given directory.
    
    Args:
        directory_path: Path to the directory containing Notion export
        
    Returns:
        Dictionary mapping clean paths to their original Notion IDs
    """
    id_map = {}
    
    for root, dirs, files in os.walk(directory_path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, directory_path)
            
            # Extract clean name and ID
            clean_name, notion_id = extract_notion_id(name)
            if notion_id:
                # Create clean path by replacing this component
                clean_rel_path = os.path.join(os.path.dirname(rel_path), clean_name)
                id_map[clean_rel_path] = notion_id
    
    return id_map

def optimize_notion_content(content: str, file_path: str) -> str:
    """
    Apply Notion-specific optimizations to content.
    
    Args:
        content: The content string to optimize
        file_path: The path of the file (for context/ID extraction)
        
    Returns:
        Optimized content string
    """
    # Extract Notion ID from filename to include in content
    filename = os.path.basename(file_path)
    clean_name, notion_id = extract_notion_id(filename)
    
    # Clean Notion artifacts
    cleaned = clean_notion_content(content)
    
    # Add Notion ID reference as HTML comment if found
    if notion_id and cleaned:
        cleaned = f"<!-- Notion ID: {notion_id} -->\n\n{cleaned}"
    
    return cleaned
