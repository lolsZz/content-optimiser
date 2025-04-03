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

# First create these imports to make them available
from .base_helper import ContentHelperBase

# Try to import each helper module
# We're using try/except blocks to avoid breaking if one module is missing
try:
    from .notion_helper import NotionHelper
except ImportError:
    class NotionHelper(ContentHelperBase):
        def __init__(self, **kwargs):
            super().__init__(name="Missing Notion Helper", **kwargs)
        def detect_content_type(self, file_path, content=None): return 0.0
        def preprocess_content(self, content, file_path=None): return content
        def optimize_content(self, content, file_path=None): return content, {}
        def postprocess_content(self, content, file_path=None): return content

try:
    from .email_helper import EmailHelper
except ImportError:
    class EmailHelper(ContentHelperBase):
        def __init__(self, **kwargs):
            super().__init__(name="Missing Email Helper", **kwargs)
        def detect_content_type(self, file_path, content=None): return 0.0
        def preprocess_content(self, content, file_path=None): return content
        def optimize_content(self, content, file_path=None): return content, {}
        def postprocess_content(self, content, file_path=None): return content

try:
    from .code_helper import CodeHelper
except ImportError:
    class CodeHelper(ContentHelperBase):
        def __init__(self, **kwargs):
            super().__init__(name="Missing Code Helper", **kwargs)
        def detect_content_type(self, file_path, content=None): return 0.0
        def preprocess_content(self, content, file_path=None): return content
        def optimize_content(self, content, file_path=None): return content, {}
        def postprocess_content(self, content, file_path=None): return content

try:
    from .docs_helper import DocsHelper
except ImportError:
    class DocsHelper(ContentHelperBase):
        def __init__(self, **kwargs):
            super().__init__(name="Missing Docs Helper", **kwargs)
        def detect_content_type(self, file_path, content=None): return 0.0
        def preprocess_content(self, content, file_path=None): return content
        def optimize_content(self, content, file_path=None): return content, {}
        def postprocess_content(self, content, file_path=None): return content

try:
    from .markdown_helper import MarkdownHelper
except ImportError:
    class MarkdownHelper(ContentHelperBase):
        def __init__(self, **kwargs):
            super().__init__(name="Missing Markdown Helper", **kwargs)
        def detect_content_type(self, file_path, content=None): return 0.0
        def preprocess_content(self, content, file_path=None): return content
        def optimize_content(self, content, file_path=None): return content, {}
        def postprocess_content(self, content, file_path=None): return content

try:
    from .unified_optimizer import UnifiedOptimizer
except ImportError:
    # This might not work as expected since we depend on all the other helpers
    class UnifiedOptimizer:
        def __init__(self, default_mode="docs", **kwargs):
            self.default_mode = default_mode
            self.config = kwargs
        def detect_content_type(self, file_path, content=None):
            return self.default_mode, 0.0
        def optimize_file(self, file_path, content=None, force_mode=None):
            return content, {"error": "UnifiedOptimizer not fully implemented"}

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
