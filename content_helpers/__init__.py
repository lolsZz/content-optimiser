"""
Content Helpers Package

This package contains specialized modules for processing different types of content:
- notion_helper: Processing Notion.so exports
- email_helper: Processing email content and threads
- code_helper: Processing source code files
- docs_helper: Processing documentation
- markdown_helper: Processing Markdown/HTML content

Each helper module provides specialized functions for detecting, cleaning, and 
optimizing its specific content type.
"""

from .base_helper import ContentHelperBase
from .notion_helper import NotionHelper
from .email_helper import EmailHelper
from .code_helper import CodeHelper  
from .docs_helper import DocsHelper
from .markdown_helper import MarkdownHelper
from .unified_optimizer import UnifiedOptimizer

# Factory function to get the appropriate helper based on content type
def get_content_helper(content_type, **kwargs):
    """
    Factory function to get an appropriate content helper instance.
    
    Args:
        content_type: String identifier for the content type 
                     ('notion', 'email', 'code', 'docs', 'markdown')
        **kwargs: Additional parameters to pass to the helper constructor
        
    Returns:
        An instance of the appropriate ContentHelperBase subclass
        
    Raises:
        ValueError: If content_type is not recognized
    """
    helpers = {
        'notion': NotionHelper,
        'email': EmailHelper,
        'code': CodeHelper,
        'docs': DocsHelper,
        'markdown': MarkdownHelper,
    }
    
    if content_type not in helpers:
        raise ValueError(f"Unknown content type: {content_type}. Available types: {', '.join(helpers.keys())}")
    
    return helpers[content_type](**kwargs)

# Function to get a unified optimizer
def get_unified_optimizer(default_mode="docs", **kwargs):
    """
    Get a UnifiedOptimizer instance that can auto-detect and optimize multiple content types.
    
    Args:
        default_mode: Default mode to use if auto-detection fails
        **kwargs: Additional parameters passed to content helpers
    
    Returns:
        A UnifiedOptimizer instance
    """
    return UnifiedOptimizer(default_mode=default_mode, **kwargs)
