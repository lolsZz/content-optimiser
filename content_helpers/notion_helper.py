"""
Helper module for processing Notion.so exports
"""

import re
import os
from pathlib import Path
import json
from collections import defaultdict

from .base_helper import ContentHelperBase

# Specialized patterns for Notion content
NOTION_ID_PATTERN = re.compile(r'([^/\\]+?)[ _]([a-f0-9]{32})(?:\.[^/\\]*)?$')
NOTION_DIVIDERS_PATTERN = re.compile(r'^---+\s*$', re.MULTILINE)
NOTION_PROPERTIES_PATTERN = re.compile(r'^(?:Property|Properties):\s*\n(?:(?:[^\n]+: [^\n]+\n)+)', re.MULTILINE)
NOTION_TIMESTAMPS_PATTERN = re.compile(r'^(?:Created|Last Edited)(?:[ :]+).*?\d{4}\s*$', re.MULTILINE)
NOTION_URL_PATTERN = re.compile(r'https://www\.notion\.so/[a-f0-9]{32}')
NOTION_COMMENTS_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
NOTION_CITATIONS_PATTERN = re.compile(r'\[(\d+)\]\(#cite-[a-f0-9-]+\)')
NOTION_CALLOUT_PATTERN = re.compile(r'>\s*(📝|💡|⚠️|ℹ️|🔍|🚫|✅|❌).*?(?:\n>.*?)*', re.MULTILINE | re.DOTALL)
NOTION_TOGGLE_PATTERN = re.compile(r'<details>.*?<summary>(.*?)</summary>.*?</details>', re.MULTILINE | re.DOTALL)

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

class NotionHelper(ContentHelperBase):
    """
    Helper for processing Notion.so exports and content
    """
    
    def __init__(self, **kwargs):
        """Initialize the Notion helper with optional config"""
        super().__init__(name="Notion", **kwargs)
        self.id_map = {}  # Map of clean paths to their Notion IDs
        self.cleaned_paths = {}  # Map of original paths to cleaned paths
        self.stats["helper_specific_data"]["notion_ids_count"] = 0
        self.stats["helper_specific_data"]["cleaned_files"] = 0
        self.stats["helper_specific_data"]["properties_converted"] = 0
        
        # Configure Notion-specific optimization settings
        self.preserve_callouts = kwargs.get('preserve_callouts', True)
        self.preserve_toggles = kwargs.get('preserve_toggles', True)
        self.include_id_comments = kwargs.get('include_id_comments', True)
        self.convert_properties = kwargs.get('convert_properties', True)
        
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file is likely from a Notion export.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is Notion content
        """
        confidence = 0.0
        
        # Check filename for Notion ID pattern
        _, notion_id = self.extract_notion_id(os.path.basename(file_path))
        if notion_id:
            confidence += 0.7
            return min(confidence, 1.0)  # Early return if strong indicator
        
        # If content was not provided, read a sample
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)  # Read first 4KB for detection
            except:
                return 0.0  # Cannot read file
        
        # Look for Notion-specific patterns in content
        if NOTION_PROPERTIES_PATTERN.search(content):
            confidence += 0.5
        
        if NOTION_TIMESTAMPS_PATTERN.search(content):
            confidence += 0.3
            
        if NOTION_URL_PATTERN.search(content):
            confidence += 0.4
            
        if NOTION_COMMENTS_PATTERN.search(content):
            confidence += 0.2
            
        if NOTION_CALLOUT_PATTERN.search(content):
            confidence += 0.2
            
        if NOTION_TOGGLE_PATTERN.search(content):
            confidence += 0.2
            
        # Cap confidence at 1.0
        return min(confidence, 1.0)
    
    def extract_notion_id(self, path):
        """
        Extract the Notion ID from a path element if present.
        
        Args:
            path: Path string possibly containing a Notion ID
            
        Returns:
            tuple: (clean_name, notion_id) where notion_id is None if not found
        """
        match = NOTION_ID_PATTERN.search(path)
        if match:
            clean_name = match.group(1).strip()
            notion_id = match.group(2)
            return (clean_name, notion_id)
        
        # No ID found, return original path and None
        return (path, None)
    
    def clean_file_path(self, path):
        """
        Clean a path by removing Notion IDs from each component.
        
        Args:
            path: Original path with possible Notion IDs
            
        Returns:
            str: Cleaned path without Notion IDs
        """
        # If we've already cleaned this path, return the cached version
        if path in self.cleaned_paths:
            return self.cleaned_paths[path]
            
        path_parts = path.split('/')
        cleaned_parts = []
        
        for part in path_parts:
            clean_name, notion_id = self.extract_notion_id(part)
            cleaned_parts.append(clean_name)
            
            # If we found an ID, record it in our map
            if notion_id:
                self.id_map['/'.join(cleaned_parts)] = notion_id
                self.stats["helper_specific_data"]["notion_ids_count"] += 1
        
        cleaned_path = '/'.join(cleaned_parts)
        self.cleaned_paths[path] = cleaned_path
        self.stats["helper_specific_data"]["cleaned_files"] += 1
        
        return cleaned_path
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare Notion content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Preprocessed content
        """
        if not content:
            return content
            
        # Extract ID from file path if available
        notion_id = None
        if file_path:
            _, notion_id = self.extract_notion_id(os.path.basename(file_path))
        
        # Add Notion ID reference as HTML comment if found and configured to do so
        if notion_id and self.include_id_comments:
            content = f"<!-- Notion ID: {notion_id} -->\n\n{content}"
            
        return content
    
    def optimize_content(self, content, file_path=None):
        """
        Apply Notion-specific optimizations to content.
        
        Args:
            content: String content to optimize
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        if not content:
            return content, {}
            
        result = content
        stats = defaultdict(int)
        
        # Process content with optimization patterns
        # Dividers (----)
        new_content, count = NOTION_DIVIDERS_PATTERN.subn('\n', result)
        if count > 0:
            result = new_content
            stats["Notion Dividers"] = count
        
        # Timestamps (Created/Edited)
        new_content, count = NOTION_TIMESTAMPS_PATTERN.subn('', result)
        if count > 0:
            result = new_content
            stats["Notion Timestamps"] = count
        
        # Notion URLs
        new_content, count = NOTION_URL_PATTERN.subn('', result)
        if count > 0:
            result = new_content
            stats["Notion URLs"] = count
        
        # Inline comments [[like this]]
        new_content, count = NOTION_COMMENTS_PATTERN.subn(r'\1', result)
        if count > 0:
            result = new_content
            stats["Notion Comments"] = count
        
        # Citation markers
        new_content, count = NOTION_CITATIONS_PATTERN.subn(r'[\1]', result)
        if count > 0:
            result = new_content
            stats["Notion Citations"] = count
        
        # Convert Notion properties to YAML frontmatter if configured
        if self.convert_properties:
            properties_match = NOTION_PROPERTIES_PATTERN.search(result)
            if properties_match:
                properties_block = properties_match.group(0)
                frontmatter = self._convert_properties_to_frontmatter(properties_block)
                
                # Replace properties block with frontmatter
                if frontmatter:
                    result = NOTION_PROPERTIES_PATTERN.sub(frontmatter + "\n\n", result)
                    stats["Notion Properties"] = 1
                    self.stats["helper_specific_data"]["properties_converted"] += 1
        
        # Handle callouts (📝, 💡, etc.) if not preserving them
        if not self.preserve_callouts:
            # Convert callouts to regular blockquotes or text
            new_content, count = NOTION_CALLOUT_PATTERN.subn(self._simplify_callout, result)
            if count > 0:
                result = new_content
                stats["Notion Callouts"] = count
        
        # Handle toggles if not preserving them
        if not self.preserve_toggles:
            # Convert toggles to headers + content
            new_content, count = NOTION_TOGGLE_PATTERN.subn(self._simplify_toggle, result)
            if count > 0:
                result = new_content
                stats["Notion Toggles"] = count
        
        # Try the specific subscription form pattern first
        if 'SUBSCRIPTION_FORM_PATTERN' in globals():
            new_content, count = SUBSCRIPTION_FORM_PATTERN.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Subscription Form"] = count
                self.stats["helper_specific_data"]["forms_removed"] = self.stats["helper_specific_data"].get("forms_removed", 0) + count
        
        # Then try the enhanced form content pattern
        if 'ENHANCED_FORM_CONTENT_PATTERN' in globals():
            new_content, count = ENHANCED_FORM_CONTENT_PATTERN.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Form Content"] = count
                self.stats["helper_specific_data"]["forms_removed"] = self.stats["helper_specific_data"].get("forms_removed", 0) + count
        
        # Remove duplicate headings (identical headings repeated consecutively)
        if 'DUPLICATE_HEADING_PATTERN' in globals():
            new_content, count = DUPLICATE_HEADING_PATTERN.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Duplicate Headings"] = count
        
        return result, dict(stats)
    
    def _simplify_callout(self, match):
        """Convert a Notion callout to simplified text"""
        callout_text = match.group(0)
        # Remove the blockquote markers and emoji
        lines = callout_text.split('\n')
        simplified_lines = []
        for line in lines:
            if line.startswith('>'):
                # Remove the '> ' and any emoji at the start of the first line
                cleaned_line = line[2:].strip()
                if simplified_lines == [] and any(emoji in cleaned_line for emoji in ['📝', '💡', '⚠️', 'ℹ️', '🔍', '🚫', '✅', '❌']):
                    # Remove the emoji from the first line
                    for emoji in ['📝', '💡', '⚠️', 'ℹ️', '🔍', '🚫', '✅', '❌']:
                        if emoji in cleaned_line:
                            cleaned_line = cleaned_line.replace(emoji, '', 1).strip()
                            break
                simplified_lines.append(cleaned_line)
        return '\n'.join(simplified_lines)
    
    def _simplify_toggle(self, match):
        """Convert a Notion toggle to simplified text"""
        summary = match.group(1)
        content = match.group(0)
        
        # Extract the content inside the details tag
        content_start = content.find('</summary>') + len('</summary>')
        content_end = content.rfind('</details>')
        if content_start >= 0 and content_end >= 0:
            inner_content = content[content_start:content_end].strip()
            # Return as a header + content
            return f"\n### {summary}\n\n{inner_content}\n"
        
        # Fallback if parsing fails
        return content
    
    def _convert_properties_to_frontmatter(self, properties_block):
        """
        Convert Notion properties block to YAML frontmatter.
        
        Args:
            properties_block: String containing the properties block
            
        Returns:
            str: YAML frontmatter
        """
        # Extract the property lines
        lines = properties_block.strip().split('\n')
        # Skip the "Properties:" header line
        property_lines = [line for line in lines if ': ' in line and not line.startswith('Properties:')]
        
        if not property_lines:
            return None
            
        frontmatter_lines = ["---"]
        
        for line in property_lines:
            # Split property name and value
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
        return "\n".join(frontmatter_lines)
    
    def postprocess_content(self, content, file_path=None):
        """
        Apply final processing after optimization.
        
        Args:
            content: String content to postprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Postprocessed content
        """
        # Perform any final cleanup
        if not content:
            return content
            
        # Ensure proper spacing
        result = content.strip()
        
        # Reduce multiple newlines to maximum of two
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
    
    def build_id_reference_table(self):
        """
        Build a Markdown table mapping clean paths to Notion IDs.
        
        Returns:
            str: Markdown table with ID reference
        """
        if not self.id_map:
            return ""
            
        lines = []
        lines.append("## Notion Content ID Reference\n")
        lines.append("| Content Path | Notion ID |")
        lines.append("|-------------|-----------|")
        
        for path, notion_id in sorted(self.id_map.items()):
            lines.append(f"| {path} | `{notion_id}` |")
            
        return "\n".join(lines) + "\n"
