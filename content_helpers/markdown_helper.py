"""
Helper module for processing Markdown/HTML content
"""

import re
import os
from pathlib import Path
from collections import defaultdict
import html
import json

from .base_helper import ContentHelperBase

# Markdown/HTML-specific patterns
MD_HTML_TAGS = re.compile(r'<(?!code|pre|script|style)([a-z][a-z0-9]*)\b[^>]*>.*?</\1>', re.IGNORECASE | re.DOTALL)
MD_HTML_COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)
MD_INLINE_HTML = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*/>|<([a-z][a-z0-9]*)\b[^>]*>(?!</)', re.IGNORECASE)
MD_FRONTMATTER = re.compile(r'^\s*---\s*\n.*?\n\s*---\s*\n', re.DOTALL)
MD_IMAGE_LINK = re.compile(r'!\[.*?\]\(.*?\)')
MD_BADGE = re.compile(r'(?:<img|!\[).*?(?:badge|shield).*?(?:>|\))')
MD_REDUNDANT_LINK = re.compile(r'\[([^\]]+)\]\(\1\)')
MD_RELATIVE_LINK = re.compile(r'\[([^\]]+)\]\((?!https?://|mailto:|ftp://|#)([^)]+)\)')
DUPLICATE_HEADING_PATTERN = re.compile(r'^(#{1,6}\s+.+)\n\1$', re.MULTILINE)
ENHANCED_FORM_CONTENT_PATTERN = re.compile(r'<form\b[^>]*>.*?</form>', re.DOTALL)

class MarkdownHelper(ContentHelperBase):
    """
    Helper for processing Markdown and HTML content
    """
    
    def __init__(self, **kwargs):
        """Initialize the Markdown helper with optional config"""
        super().__init__(name="Markdown", **kwargs)
        
        # Configure markdown-specific optimization settings
        self.preserve_html = kwargs.get('preserve_html', True)
        self.preserve_comments = kwargs.get('preserve_comments', False)
        self.preserve_images = kwargs.get('preserve_images', True)
        self.preserve_badges = kwargs.get('preserve_badges', False)
        self.preserve_frontmatter = kwargs.get('preserve_frontmatter', True)
        self.fix_redundant_links = kwargs.get('fix_redundant_links', True)
        self.fix_relative_links = kwargs.get('fix_relative_links', False)
        
        # Markdown-specific statistics
        self.stats["helper_specific_data"]["html_tags_removed"] = 0
        self.stats["helper_specific_data"]["html_comments_removed"] = 0
        self.stats["helper_specific_data"]["frontmatter_removed"] = 0
        self.stats["helper_specific_data"]["images_removed"] = 0
        self.stats["helper_specific_data"]["badges_removed"] = 0
        self.stats["helper_specific_data"]["redundant_links_fixed"] = 0
        self.stats["helper_specific_data"]["relative_links_fixed"] = 0
        self.stats["helper_specific_data"]["duplicate_headings_removed"] = 0
        self.stats["helper_specific_data"]["forms_removed"] = 0
    
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file contains Markdown/HTML content.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is Markdown/HTML
        """
        confidence = 0.0
        
        # Check file extension first
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.md', '.markdown', '.htm', '.html']:
            confidence += 0.8
            return min(confidence, 1.0)  # Strong indicator
        
        # If content was not provided, read a sample
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)  # Read first 4KB for detection
            except:
                return 0.0  # Cannot read file
        
        # Look for markdown/HTML patterns in content
        
        # Check for markdown headers
        if re.search(r'^#{1,6}\s+\w+', content, re.MULTILINE):
            confidence += 0.5
        
        # Check for markdown links
        if re.search(r'\[.*?\]\(.*?\)', content):
            confidence += 0.4
        
        # Check for HTML tags
        if re.search(r'<[a-z][a-z0-9]*\b[^>]*>.*?</[a-z][a-z0-9]*>', content, re.IGNORECASE | re.DOTALL):
            confidence += 0.6
        
        # Check for markdown list items
        if re.search(r'^(?:[*+-]|\d+\.)\s+\w+', content, re.MULTILINE):
            confidence += 0.3
        
        # Check for markdown emphasis/bold
        if re.search(r'\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_', content):
            confidence += 0.2
        
        # Check for frontmatter
        if re.match(MD_FRONTMATTER, content):
            confidence += 0.5
        
        # Check for code blocks
        if re.search(r'```\w*\n[\s\S]*?```', content):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare Markdown content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            dict: Preprocessed content with metadata
        """
        if not content:
            return {'content': '', 'has_frontmatter': False}
        
        # Check for frontmatter
        has_frontmatter = bool(re.match(MD_FRONTMATTER, content))
        
        # Count HTML tags, comments, and images for statistics
        html_tags = re.findall(MD_HTML_TAGS, content)
        html_comments = re.findall(MD_HTML_COMMENT, content)
        images = re.findall(MD_IMAGE_LINK, content)
        badges = re.findall(MD_BADGE, content)
        
        # Return content with metadata
        return {
            'content': content,
            'has_frontmatter': has_frontmatter,
            'html_tags_count': len(html_tags),
            'html_comments_count': len(html_comments),
            'images_count': len(images),
            'badges_count': len(badges),
            'file_path': file_path
        }
    
    def optimize_content(self, content_data, file_path=None):
        """
        Apply Markdown-specific optimizations.
        
        Args:
            content_data: Preprocessed content dictionary or raw string
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        if not isinstance(content_data, dict):
            # Handle case where content wasn't preprocessed
            content = content_data
        else:
            content = content_data['content']
            file_path = content_data.get('file_path', file_path)
        
        if not content:
            return content, {}
        
        result = content
        stats = defaultdict(int)
        
        # Remove frontmatter unless configured to keep
        if not self.preserve_frontmatter:
            new_content, count = MD_FRONTMATTER.subn('', result)
            if count > 0:
                result = new_content
                stats["Markdown Frontmatter Removed"] = count
                self.stats["helper_specific_data"]["frontmatter_removed"] += count
        
        # Remove HTML tags unless configured to keep
        if not self.preserve_html:
            new_content, count = MD_HTML_TAGS.subn('', result)
            if count > 0:
                result = new_content
                stats["HTML Tags Removed"] = count
                self.stats["helper_specific_data"]["html_tags_removed"] += count
            
            # Also handle inline HTML tags
            new_content, count = MD_INLINE_HTML.subn('', result)
            if count > 0:
                result = new_content
                stats["Inline HTML Tags Removed"] = count
                self.stats["helper_specific_data"]["html_tags_removed"] += count
        
        # Remove HTML comments unless configured to keep
        if not self.preserve_comments:
            new_content, count = MD_HTML_COMMENT.subn('', result)
            if count > 0:
                result = new_content
                stats["HTML Comments Removed"] = count
                self.stats["helper_specific_data"]["html_comments_removed"] += count
        
        # Remove images unless configured to keep
        if not self.preserve_images:
            new_content, count = MD_IMAGE_LINK.subn('', result)
            if count > 0:
                result = new_content
                stats["Image Links Removed"] = count
                self.stats["helper_specific_data"]["images_removed"] += count
        
        # Always remove badges unless specifically configured to keep
        if not self.preserve_badges:
            new_content, count = MD_BADGE.subn('', result)
            if count > 0:
                result = new_content
                stats["Badges Removed"] = count
                self.stats["helper_specific_data"]["badges_removed"] += count
        
        # Fix redundant links ([http://example.com](http://example.com) -> http://example.com)
        if self.fix_redundant_links:
            new_content, count = MD_REDUNDANT_LINK.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Redundant Links Fixed"] = count
                self.stats["helper_specific_data"]["redundant_links_fixed"] += count
        
        # Fix relative links if configured (point them to base path or use text only)
        if self.fix_relative_links:
            # Just use the link text and remove the relative URL
            new_content, count = MD_RELATIVE_LINK.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Relative Links Fixed"] = count
                self.stats["helper_specific_data"]["relative_links_fixed"] += count
        
        # Remove duplicate headings (identical headings repeated consecutively)
        new_content, count = DUPLICATE_HEADING_PATTERN.subn(r'\1', result)
        if count > 0:
            result = new_content
            stats["Duplicate Headings Removed"] = count
            self.stats["helper_specific_data"]["duplicate_headings_removed"] += count
        
        # Handle enhanced form content pattern
        new_content, count = ENHANCED_FORM_CONTENT_PATTERN.subn('', result)
        if count > 0:
            result = new_content
            stats["Form Content Removed"] = count
            self.stats["helper_specific_data"]["forms_removed"] += count
        
        return result, dict(stats)
    
    def postprocess_content(self, content, file_path=None):
        """
        Apply final processing after optimization.
        
        Args:
            content: String content to postprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Postprocessed content
        """
        if not content:
            return content
        
        # Clean up spacing between sections
        result = content.strip()
        
        # Replace multiple consecutive blank lines with a maximum of two
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
