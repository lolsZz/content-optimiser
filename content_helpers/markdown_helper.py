"""
Markdown/MDC/CursorRules Content Helper

Specialized helper for processing Markdown, MDC, and CursorRules content, 
which are similar formats with specific conventions.
"""

import re
from pathlib import Path
from .base_helper import ContentHelperBase

class MarkdownHelper(ContentHelperBase):
    """
    Helper for processing Markdown, MDC, and CursorRules files.
    Handles specialized formatting and conventions in these files.
    """
    
    def __init__(self, **kwargs):
        """Initialize the Markdown helper."""
        super().__init__(name="Markdown Helper", **kwargs)
        self.config = {
            "preserve_frontmatter": kwargs.get("preserve_frontmatter", True),
            "preserve_code_blocks": kwargs.get("preserve_code_blocks", True),
            "preserve_tables": kwargs.get("preserve_tables", True),
            "preserve_links": kwargs.get("preserve_links", True),
            "preserve_images": kwargs.get("preserve_images", True),
            "fix_redundant_links": kwargs.get("fix_redundant_links", True),
            "preserve_badges": kwargs.get("preserve_badges", False),
            "preserve_html": kwargs.get("preserve_html", True),
            "preserve_comments": kwargs.get("preserve_comments", False),
            "fix_relative_links": kwargs.get("fix_relative_links", False),
        }
        
        # Initialize statistics
        self.stats = {
            "helper_name": self.name,
            "helper_specific_data": {
                "frontmatter_preserved": 0,
                "code_blocks_preserved": 0,
                "tables_preserved": 0,
                "links_preserved": 0,
                "images_preserved": 0,
                "redundant_links_fixed": 0,
                "relative_links_fixed": 0,
                "html_blocks_preserved": 0,
                "comments_preserved": 0,
            },
            "files_processed": 0,
        }
        
        # Patterns for parsing
        self.frontmatter_pattern = re.compile(r'^\s*---\s*\n.*?\n\s*---\s*\n', re.DOTALL)
        self.code_block_pattern = re.compile(r'```(?:[a-zA-Z0-9]*)\n.*?```', re.DOTALL)
        self.table_pattern = re.compile(r'\n\s*\|.*?\|.*?\n(?:\s*\|[-:]+\|[-:]+\|\n)(?:\s*\|.*?\|.*?\n)+', re.DOTALL)
        self.image_pattern = re.compile(r'!\[.*?\]\(.*?\)')
        self.link_pattern = re.compile(r'(?<!!)\[.*?\]\(.*?\)')
        self.html_block_pattern = re.compile(r'<[a-zA-Z]+[^>]*>.*?</[a-zA-Z]+>', re.DOTALL)
        self.html_comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
        self.badge_pattern = re.compile(r'!\[.*?\]\(https?://(?:img\.shields\.io|shields\.io|badge\.fury\.io).*?\)')
        
        # MDC/CursorRules specific patterns
        self.mdc_frontmatter_pattern = re.compile(r'^\s*---\s*\n.*?globs:.*?\n\s*---\s*\n', re.DOTALL)
        self.cursorrules_properties_pattern = re.compile(r'^\s*(?:description|globs|mode|scope|options):\s*.*?$', re.MULTILINE)
        
    def detect_content_type(self, file_path, content=None):
        """
        Determine if this helper should process the given file.
        
        Args:
            file_path: Path to the file
            content: Optional file content if already read
            
        Returns:
            float: Confidence score between 0 and 1
        """
        if not file_path:
            return 0.0
        
        file_path = str(file_path).lower()
        
        # Check extensions first for quick decisions
        if file_path.endswith('.md'):
            return 0.9
        elif file_path.endswith('.mdc'):
            return 0.95
        elif file_path.endswith('.cursorrules'):
            return 0.95
        elif file_path.endswith('.markdown'):
            return 0.9
        
        # If content is available, do deeper inspection
        if content:
            # Check for markdown indicators
            if self.frontmatter_pattern.search(content):
                return 0.8
            if '```' in content and self.code_block_pattern.search(content):
                return 0.7
            if '#' in content and re.search(r'^#+\s+\w+', content, re.MULTILINE):
                return 0.6
            if self.link_pattern.search(content) or self.image_pattern.search(content):
                return 0.5
                
            # MDC/CursorRules specific checks
            if self.mdc_frontmatter_pattern.search(content):
                return 0.9
            if self.cursorrules_properties_pattern.search(content):
                return 0.85
        
        return 0.1
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare markdown content for optimization.
        
        Args:
            content: The raw content to process
            file_path: Path to the source file
            
        Returns:
            dict: Processed content with metadata
        """
        if not content:
            return {"content": "", "metadata": {}}
        
        # Extract and preserve frontmatter if configured
        frontmatter = None
        content_without_frontmatter = content
        
        if self.config["preserve_frontmatter"]:
            match = self.frontmatter_pattern.search(content)
            if match:
                frontmatter = match.group(0)
                content_without_frontmatter = content[match.end():]
                self.stats["helper_specific_data"]["frontmatter_preserved"] += 1
        
        # Check for MDC/CursorRules frontmatter specifically
        is_mdc = False
        is_cursorrules = False
        
        if file_path:
            if str(file_path).lower().endswith('.mdc'):
                is_mdc = True
            elif str(file_path).lower().endswith('.cursorrules'):
                is_cursorrules = True
                
        if is_mdc or is_cursorrules:
            match = self.mdc_frontmatter_pattern.search(content)
            if match:
                frontmatter = match.group(0)
                content_without_frontmatter = content[match.end():]
                self.stats["helper_specific_data"]["frontmatter_preserved"] += 1
        
        # Store code blocks for later restoration if configured
        code_blocks = []
        if self.config["preserve_code_blocks"]:
            for i, match in enumerate(self.code_block_pattern.finditer(content_without_frontmatter)):
                code_blocks.append((f"CODE_BLOCK_{i}", match.group(0)))
                self.stats["helper_specific_data"]["code_blocks_preserved"] += 1
            
            # Replace code blocks with placeholders
            for placeholder, block in code_blocks:
                content_without_frontmatter = content_without_frontmatter.replace(block, placeholder)
        
        # Store tables for later restoration if configured
        tables = []
        if self.config["preserve_tables"]:
            for i, match in enumerate(self.table_pattern.finditer(content_without_frontmatter)):
                tables.append((f"TABLE_{i}", match.group(0)))
                self.stats["helper_specific_data"]["tables_preserved"] += 1
            
            # Replace tables with placeholders
            for placeholder, table in tables:
                content_without_frontmatter = content_without_frontmatter.replace(table, placeholder)
        
        # Store HTML blocks for later restoration if configured
        html_blocks = []
        if self.config["preserve_html"]:
            for i, match in enumerate(self.html_block_pattern.finditer(content_without_frontmatter)):
                html_blocks.append((f"HTML_BLOCK_{i}", match.group(0)))
                self.stats["helper_specific_data"]["html_blocks_preserved"] += 1
            
            # Replace HTML blocks with placeholders
            for placeholder, block in html_blocks:
                content_without_frontmatter = content_without_frontmatter.replace(block, placeholder)
        
        # Store HTML comments for later restoration if configured
        html_comments = []
        if self.config["preserve_comments"]:
            for i, match in enumerate(self.html_comment_pattern.finditer(content_without_frontmatter)):
                html_comments.append((f"HTML_COMMENT_{i}", match.group(0)))
                self.stats["helper_specific_data"]["comments_preserved"] += 1
            
            # Replace HTML comments with placeholders
            for placeholder, comment in html_comments:
                content_without_frontmatter = content_without_frontmatter.replace(comment, placeholder)
        
        # Store images for later restoration if configured
        images = []
        if self.config["preserve_images"]:
            for i, match in enumerate(self.image_pattern.finditer(content_without_frontmatter)):
                # Skip badges if not preserving them
                if not self.config["preserve_badges"] and self.badge_pattern.match(match.group(0)):
                    continue
                    
                images.append((f"IMAGE_{i}", match.group(0)))
                self.stats["helper_specific_data"]["images_preserved"] += 1
            
            # Replace images with placeholders
            for placeholder, image in images:
                content_without_frontmatter = content_without_frontmatter.replace(image, placeholder)
        
        # Store links for later restoration if configured
        links = []
        if self.config["preserve_links"]:
            for i, match in enumerate(self.link_pattern.finditer(content_without_frontmatter)):
                links.append((f"LINK_{i}", match.group(0)))
                self.stats["helper_specific_data"]["links_preserved"] += 1
            
            # Replace links with placeholders
            for placeholder, link in links:
                content_without_frontmatter = content_without_frontmatter.replace(link, placeholder)
        
        # Return the processed content with metadata
        return {
            "content": content_without_frontmatter,
            "metadata": {
                "frontmatter": frontmatter,
                "code_blocks": code_blocks,
                "tables": tables,
                "html_blocks": html_blocks,
                "html_comments": html_comments,
                "images": images,
                "links": links,
                "is_mdc": is_mdc,
                "is_cursorrules": is_cursorrules,
                "file_path": file_path
            }
        }
    
    def optimize_content(self, content_data, file_path=None):
        """
        Optimize markdown content by applying rules.
        
        Args:
            content_data: Preprocessed content data dictionary
            file_path: Path to the source file
            
        Returns:
            (str, dict): Tuple of (optimized_content, stats)
        """
        # Get the preprocessed content
        content = content_data.get("content", "")
        metadata = content_data.get("metadata", {})
        
        # Check if this is a special file type
        is_mdc = metadata.get("is_mdc", False)
        is_cursorrules = metadata.get("is_cursorrules", False)
        
        # Apply optimization rules - more conservative for MDC/CursorRules files
        try:
            import optimization_rules
            rule_trigger_stats = {}
            
            for rule_name, pattern in optimization_rules.OPTIMIZATION_RULES_ORDERED:
                # Skip certain aggressive rules for MDC/CursorRules files
                if (is_mdc or is_cursorrules) and rule_name in [
                    "WP Nav List", "WP Sidebar Sections", "WP Slider Nav",
                    "Consecutive Markdown Link List", "Simple Text Nav Menu"
                ]:
                    continue
                    
                # Apply the rule
                content_before = content
                content = pattern.sub('', content)
                
                # Track whether the rule was applied
                if content != content_before:
                    rule_trigger_stats[rule_name] = rule_trigger_stats.get(rule_name, 0) + 1
        except ImportError:
            # If rules module isn't available, use minimal cleanup
            # Remove excessive newlines
            content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix redundant links if configured
        if self.config["fix_redundant_links"]:
            # Pattern: [Some text](url) where text is the same as url
            redundant_links_pattern = re.compile(r'\[(https?://[^\]]+)\]\(\1\)')
            content_before = content
            content = redundant_links_pattern.sub(r'\1', content)
            if content != content_before:
                self.stats["helper_specific_data"]["redundant_links_fixed"] += 1
        
        # Fix relative links if configured
        if self.config["fix_relative_links"]:
            # Convert relative links to text except for anchors
            relative_links_pattern = re.compile(r'\[([^\]]+)\]\((?!https?://|#)([^)]+)\)')
            content_before = content
            content = relative_links_pattern.sub(r'\1', content)
            if content != content_before:
                self.stats["helper_specific_data"]["relative_links_fixed"] += 1
        
        # Update statistics
        stats = {
            "optimized_content": content,
            "rule_trigger_stats": rule_trigger_stats
        }
        
        return content, stats
    
    def postprocess_content(self, content, file_path=None):
        """
        Restore preserved elements and finalize the content.
        
        Args:
            content: The optimized content
            file_path: Path to the source file
            
        Returns:
            str: The finalized content
        """
        if not hasattr(self, '_preprocessed_data') or not self._preprocessed_data:
            return content
            
        metadata = self._preprocessed_data.get("metadata", {})
        
        # Restore links
        links = metadata.get("links", [])
        for placeholder, link in links:
            content = content.replace(placeholder, link)
        
        # Restore images
        images = metadata.get("images", [])
        for placeholder, image in images:
            content = content.replace(placeholder, image)
        
        # Restore HTML comments
        html_comments = metadata.get("html_comments", [])
        for placeholder, comment in html_comments:
            content = content.replace(placeholder, comment)
        
        # Restore HTML blocks
        html_blocks = metadata.get("html_blocks", [])
        for placeholder, block in html_blocks:
            content = content.replace(placeholder, block)
        
        # Restore tables
        tables = metadata.get("tables", [])
        for placeholder, table in tables:
            content = content.replace(placeholder, table)
        
        # Restore code blocks
        code_blocks = metadata.get("code_blocks", [])
        for placeholder, block in code_blocks:
            content = content.replace(placeholder, block)
        
        # Restore frontmatter
        frontmatter = metadata.get("frontmatter")
        if frontmatter:
            content = frontmatter + content
        
        # Final cleanup - remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Track this file as processed
        self.stats["files_processed"] += 1
        
        return content
    
    def process_file(self, file_path, content=None):
        """
        Process a markdown file from start to finish.
        
        Args:
            file_path: Path to the file
            content: Optional content if already read
            
        Returns:
            (str, dict): Tuple of (processed_content, stats)
        """
        # Read the file if content not provided
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return f"Error reading file: {e}", {"error": str(e)}
        
        # Process in stages
        preprocessed = self.preprocess_content(content, file_path)
        self._preprocessed_data = preprocessed  # Store for postprocessing
        
        optimized_content, optimization_stats = self.optimize_content(preprocessed, file_path)
        final_content = self.postprocess_content(optimized_content, file_path)
        
        # Combine stats
        stats = {**self.stats, **optimization_stats}
        
        return final_content, stats
    
    def get_stats(self):
        """Get the current statistics."""
        return self.stats
