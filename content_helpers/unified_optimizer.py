"""
Unified interface for content optimization using specialized helpers
"""
from collections import defaultdict
from pathlib import Path

from . import get_content_helper
from .base_helper import ContentHelperBase

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
            "docs": get_content_helper("docs")(),
            "code": get_content_helper("code")(),
            "notion": get_content_helper("notion")(),
            "email": get_content_helper("email")(),
            "markdown": get_content_helper("markdown")()
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
        
        combined_stats = {**self.stats}
        if isinstance(stats, dict):
            for key, value in stats.items():
                if key in combined_stats and isinstance(value, dict) and isinstance(combined_stats[key], dict):
                    combined_stats[key].update(value)
                else:
                    combined_stats[key] = value
        
        return optimized_content, combined_stats
    
    def get_stats(self):
        """Get the current statistics."""
        return self.stats
