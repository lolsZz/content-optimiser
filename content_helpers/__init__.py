"""
Content Helpers Package for Content Optimizer

This package contains specialized helpers for different content types.
"""

# Import the base helper class
from .base_helper import ContentHelperBase

# Dummy helper implementations for now - these will be replaced by actual implementations
class DocsHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="Docs Helper", **kwargs)
    
    def detect_content_type(self, file_path, content=None):
        return 0.5 if file_path else 0.0
    
    def preprocess_content(self, content, file_path=None):
        return {"content": content, "metadata": {}}
    
    def optimize_content(self, content_data, file_path=None):
        return content_data.get("content", ""), {}
    
    def postprocess_content(self, content, file_path=None):
        return content

class CodeHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="Code Helper", **kwargs)
    
    def detect_content_type(self, file_path, content=None):
        return 0.5 if file_path else 0.0
    
    def preprocess_content(self, content, file_path=None):
        return {"content": content, "metadata": {}}
    
    def optimize_content(self, content_data, file_path=None):
        return content_data.get("content", ""), {}
    
    def postprocess_content(self, content, file_path=None):
        return content

class NotionHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="Notion Helper", **kwargs)
    
    def detect_content_type(self, file_path, content=None):
        return 0.5 if file_path else 0.0
    
    def preprocess_content(self, content, file_path=None):
        return {"content": content, "metadata": {}}
    
    def optimize_content(self, content_data, file_path=None):
        return content_data.get("content", ""), {}
    
    def postprocess_content(self, content, file_path=None):
        return content

class EmailHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="Email Helper", **kwargs)
    
    def detect_content_type(self, file_path, content=None):
        return 0.5 if file_path else 0.0
    
    def preprocess_content(self, content, file_path=None):
        return {"content": content, "metadata": {}}
    
    def optimize_content(self, content_data, file_path=None):
        return content_data.get("content", ""), {}
    
    def postprocess_content(self, content, file_path=None):
        return content

# Use our existing markdown helper that was already implemented
from .markdown_helper import MarkdownHelper

# Unified optimizer for auto-detection
class UnifiedOptimizer:
    """
    A unified optimizer that can detect content type and apply the appropriate helper.
    """
    
    def __init__(self, default_mode="auto"):
        """
        Initialize the unified optimizer.
        
        Args:
            default_mode: Default mode to use if type detection fails
        """
        self.default_mode = default_mode
        self.helpers = {
            "docs": DocsHelper(),
            "code": CodeHelper(),
            "notion": NotionHelper(),
            "email": EmailHelper(),
            "markdown": MarkdownHelper()
        }
        self.stats = {
            "files_processed": 0,
            "detection": {}
        }
    
    def detect_content_type(self, file_path, content=None):
        """
        Detect the content type of a file.
        
        Args:
            file_path: Path to the file
            content: Optional file content if already loaded
            
        Returns:
            Tuple of (type, confidence, helper)
        """
        best_type = None
        best_confidence = 0.0
        best_helper = None
        
        for helper_type, helper in self.helpers.items():
            confidence = helper.detect_content_type(file_path, content)
            if confidence > best_confidence:
                best_type = helper_type
                best_confidence = confidence
                best_helper = helper
        
        if best_type is None:
            best_type = self.default_mode
            best_helper = self.helpers.get(self.default_mode, self.helpers["docs"])
        
        return best_type, best_confidence, best_helper
    
    def optimize_file(self, file_path, content=None):
        """
        Optimize a file by detecting its type and using the appropriate helper.
        
        Args:
            file_path: Path to the file
            content: Optional file content if already loaded
            
        Returns:
            Tuple of (optimized_content, stats)
        """
        # Read the file if content not provided
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return f"Error reading file: {e}", {"error": str(e)}
        
        # Detect content type
        content_type, confidence, helper = self.detect_content_type(file_path, content)
        
        # Process with the appropriate helper
        optimized_content, stats = helper.process_file(file_path, content)
        
        # Update stats
        self.stats["files_processed"] += 1
        self.stats["detection"][file_path] = {
            "type": content_type,
            "confidence": confidence
        }
        
        combined_stats = {**self.stats, **stats}
        
        return optimized_content, combined_stats
    
    def get_stats(self):
        """Get the current statistics."""
        return self.stats

# Factory functions
def get_content_helper(name):
    """
    Factory function to get a specific content helper.
    
    Args:
        name: Name of the helper to get (docs, code, notion, email, markdown)
        
    Returns:
        The helper class
    """
    helpers = {
        "docs": DocsHelper,
        "code": CodeHelper,
        "notion": NotionHelper,
        "email": EmailHelper,
        "markdown": MarkdownHelper
    }
    
    if name not in helpers:
        raise ValueError(f"Unknown helper name: {name}. Available helpers: {', '.join(helpers.keys())}")
    
    return helpers[name]

def get_unified_optimizer(default_mode="auto"):
    """
    Get a unified optimizer instance.
    
    Args:
        default_mode: Default mode to use if type detection fails
        
    Returns:
        UnifiedOptimizer instance
    """
    return UnifiedOptimizer(default_mode=default_mode)
