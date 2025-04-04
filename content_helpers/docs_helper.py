"""
Helper module for processing documentation content
"""

import re
import os
from pathlib import Path
import json
from collections import defaultdict

from .base_helper import ContentHelperBase

# Documentation-specific patterns
DOC_HEADER_PATTERN = re.compile(r'^#+\s+(.*?)$', re.MULTILINE)
DOC_CODE_BLOCK_PATTERN = re.compile(r'```[\w]*\n.*?```', re.DOTALL)
DOC_TABLE_PATTERN = re.compile(r'^\|.*\|$(?:\n\|[-:| ]+\|$)?(?:\n\|.*\|$)*', re.MULTILINE)
DOC_NAV_BREADCRUMB = re.compile(r'^(?:Home|Index|Main)(?:\s+[>→←/|])+.*?$', re.MULTILINE)
DOC_VERSION_BANNER = re.compile(r'^(?:Version|v|Release):\s+\d+\.\d+(?:\.\d+)?.*?$', re.MULTILINE)
DOC_EDIT_BANNER = re.compile(r'^(?:Last updated|Last modified|Updated on):\s+.*?$', re.MULTILINE)
DOC_TOC_SECTION = re.compile(r'(?:Table of Contents|Contents|TOC|On this page)[\s\n]*(?:\*\s+\[.*?\]\(.*?\)[\s\n]*)+', re.IGNORECASE)

class DocsHelper(ContentHelperBase):
    """
    Helper for processing documentation content
    """
    
    def __init__(self, **kwargs):
        """Initialize the Documentation helper with optional config"""
        super().__init__(name="Documentation", **kwargs)
        
        # Configure docs-specific optimization settings
        self.preserve_toc = kwargs.get('preserve_toc', True)
        self.preserve_breadcrumbs = kwargs.get('preserve_breadcrumbs', False)
        self.preserve_edit_info = kwargs.get('preserve_edit_info', False)
        self.preserve_version_info = kwargs.get('preserve_version_info', True)
        
        # Docs-specific statistics
        self.stats["helper_specific_data"]["headers_found"] = 0
        self.stats["helper_specific_data"]["code_blocks_found"] = 0
        self.stats["helper_specific_data"]["tables_found"] = 0
        self.stats["helper_specific_data"]["toc_removed"] = 0
        self.stats["helper_specific_data"]["breadcrumbs_removed"] = 0
        self.stats["helper_specific_data"]["edit_info_removed"] = 0
        self.stats["helper_specific_data"]["version_info_removed"] = 0
    
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file contains documentation content.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is documentation
        """
        confidence = 0.0
        
        # Check file extension first
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.md', '.rst', '.txt', '.adoc', '.asciidoc']:
            confidence += 0.6
            
            # Extra boost for common documentation file names
            basename = Path(file_path).stem.lower()
            if basename in ['readme', 'guide', 'tutorial', 'manual', 'introduction', 
                           'getting-started', 'docs', 'documentation', 'reference',
                           'handbook', 'specification', 'api', 'help']:
                confidence += 0.3
                return min(confidence, 1.0)  # Strong indicator
        
        # If content was not provided, read a sample
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)  # Read first 4KB for detection
            except:
                return 0.0  # Cannot read file
        
        # Look for markdown/docs patterns in content
        
        # Check for headers
        headers = re.findall(DOC_HEADER_PATTERN, content)
        if headers:
            confidence += 0.3
            # Extra points if there's a good header hierarchy (multiple header levels)
            header_levels = set(re.findall(r'^(#+)\s+', content, re.MULTILINE))
            if len(header_levels) > 1:
                confidence += 0.2
        
        # Check for code blocks
        code_blocks = re.findall(DOC_CODE_BLOCK_PATTERN, content)
        if code_blocks:
            confidence += 0.2
        
        # Check for tables
        tables = re.findall(DOC_TABLE_PATTERN, content)
        if tables:
            confidence += 0.2
        
        # Check for table of contents
        if re.search(DOC_TOC_SECTION, content):
            confidence += 0.3
        
        # Check for inline formatting (bold, italics, links)
        if re.search(r'\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[.*?\]\(.*?\)', content):
            confidence += 0.2
        
        # Check for list items
        if re.search(r'^(?:[*+-]|\d+\.)\s+', content, re.MULTILINE):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare documentation content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            dict: Preprocessed content with metadata
        """
        if not content:
            return {'content': '', 'headers': [], 'code_blocks': []}
        
        # Extract and count headers
        headers = re.findall(DOC_HEADER_PATTERN, content)
        self.stats["helper_specific_data"]["headers_found"] += len(headers)
        
        # Extract and count code blocks (save content to preserve during optimization)
        code_blocks = []
        code_block_matches = re.finditer(DOC_CODE_BLOCK_PATTERN, content)
        for match in code_block_matches:
            code_blocks.append(match.group(0))
        self.stats["helper_specific_data"]["code_blocks_found"] += len(code_blocks)
        
        # Extract and count tables
        tables = re.findall(DOC_TABLE_PATTERN, content)
        self.stats["helper_specific_data"]["tables_found"] += len(tables)
        
        # Return content with extracted metadata
        return {
            'content': content,
            'headers': headers,
            'code_blocks': code_blocks,
            'tables': tables,
            'file_path': file_path
        }
    
    def optimize_content(self, content_data, file_path=None):
        """
        Apply documentation-specific optimizations to content.
        
        Args:
            content_data: Dictionary with content and metadata from preprocessing
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        # Extract content from data structure
        content = content_data.get('content', '')
        if not content:
            return content, {}
            
        result = content
        stats = defaultdict(int)
        code_blocks = content_data.get('code_blocks', [])
        
        # Replace code blocks with placeholders to protect them during optimization
        code_block_placeholders = {}
        if code_blocks:
            for i, block in enumerate(code_blocks):
                placeholder = f"__CODE_BLOCK_{i}__"
                code_block_placeholders[placeholder] = block
                result = result.replace(block, placeholder)
        
        # Remove duplicate headings (identical headings repeated consecutively)
        new_content, count = DUPLICATE_HEADING_PATTERN.subn(r'\1', result) if 'DUPLICATE_HEADING_PATTERN' in globals() else (result, 0)
        if count > 0:
            result = new_content
            stats["Duplicate Headings Removed"] = count
            self.stats["helper_specific_data"]["duplicate_headings_removed"] = self.stats["helper_specific_data"].get("duplicate_headings_removed", 0) + count
        
        # Handle enhanced form content pattern
        if 'ENHANCED_FORM_CONTENT_PATTERN' in globals():
            new_content, count = ENHANCED_FORM_CONTENT_PATTERN.subn(r'\1', result)
            if count > 0:
                result = new_content
                stats["Form Content Removed"] = count
                self.stats["helper_specific_data"]["forms_removed"] = self.stats["helper_specific_data"].get("forms_removed", 0) + count
                
        # Remove table of contents unless configured to keep
        if not self.preserve_toc:
            new_content, count = DOC_TOC_SECTION.subn('', result)
            if count > 0:
                result = new_content
                stats["Doc TOC Removed"] = count
                self.stats["helper_specific_data"]["toc_removed"] += count
        
        # Remove navigation breadcrumbs unless configured to keep
        if not self.preserve_breadcrumbs:
            new_content, count = DOC_NAV_BREADCRUMB.subn('', result)
            if count > 0:
                result = new_content
                stats["Doc Breadcrumbs Removed"] = count
                self.stats["helper_specific_data"]["breadcrumbs_removed"] += count
        
        # Remove edit information unless configured to keep
        if not self.preserve_edit_info:
            new_content, count = DOC_EDIT_BANNER.subn('', result)
            if count > 0:
                result = new_content
                stats["Doc Edit Info Removed"] = count
                self.stats["helper_specific_data"]["edit_info_removed"] += count
        
        # Remove version information unless configured to keep
        if not self.preserve_version_info:
            new_content, count = DOC_VERSION_BANNER.subn('', result)
            if count > 0:
                result = new_content
                stats["Doc Version Info Removed"] = count
                self.stats["helper_specific_data"]["version_info_removed"] += count
        
        # Restore code blocks from placeholders
        for placeholder, block in code_block_placeholders.items():
            result = result.replace(placeholder, block)
        
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
        
        # Ensure proper spacing between sections
        # Replace multiple blank lines with at most two
        result = re.sub(r'\n{3,}', '\n\n', content.strip())
        
        # Ensure proper spacing after headers
        result = re.sub(r'(^#+\s+.*?)(\n)(?!\n)', r'\1\n\n', result, flags=re.MULTILINE)
        
        return result
