"""
Base Helper Class for Content Optimizer

This module defines the abstract base class that all content helpers must implement.
"""

from abc import ABC, abstractmethod

class ContentHelperBase(ABC):
    """
    Abstract base class for content helpers.
    
    Content helpers are specialized classes that process different types of content,
    such as documentation, code, Notion exports, email, etc.
    """
    
    def __init__(self, name="Base Helper", **kwargs):
        """
        Initialize the base helper with a name and optional configuration.
        
        Args:
            name: Name of the helper
            **kwargs: Additional configuration options
        """
        self.name = name
        self.config = kwargs
        self.stats = {
            "helper_name": self.name,
            "files_processed": 0,
            "helper_specific_data": {}
        }
    
    @abstractmethod
    def detect_content_type(self, file_path, content=None) -> float:
        """
        Detect if this content type matches what this helper can process.
        
        Args:
            file_path: Path to the file
            content: Optional file content if already loaded
            
        Returns:
            Confidence score from 0.0 to 1.0
        """
        pass
    
    @abstractmethod
    def preprocess_content(self, content, file_path=None) -> dict:
        """
        Preprocess content before optimization.
        
        Args:
            content: Raw content to preprocess
            file_path: Optional path to the source file
            
        Returns:
            Dict with processed content and metadata
        """
        pass
    
    @abstractmethod
    def optimize_content(self, content_data, file_path=None) -> tuple:
        """
        Apply content-specific optimizations.
        
        Args:
            content_data: Content data from preprocessing
            file_path: Optional path to the source file
            
        Returns:
            Tuple of (optimized_content, stats)
        """
        pass
    
    @abstractmethod
    def postprocess_content(self, content, file_path=None) -> str:
        """
        Apply final processing to optimized content.
        
        Args:
            content: Optimized content
            file_path: Optional path to the source file
            
        Returns:
            Final processed content
        """
        pass
    
    def process_file(self, file_path, content=None) -> tuple:
        """
        Process a file from start to finish.
        
        This is the main method that orchestrates the processing pipeline.
        
        Args:
            file_path: Path to the file
            content: Optional file content if already loaded
            
        Returns:
            Tuple of (processed_content, stats)
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
        
        if hasattr(self, '_store_preprocessed_data'):
            self._preprocessed_data = preprocessed
            
        optimized_content, optimization_stats = self.optimize_content(preprocessed, file_path)
        final_content = self.postprocess_content(optimized_content, file_path)
        
        # Update statistics
        self.stats["files_processed"] += 1
        
        # Combine stats
        combined_stats = {**self.stats}
        if isinstance(optimization_stats, dict):
            for key, value in optimization_stats.items():
                if key in combined_stats and isinstance(value, dict) and isinstance(combined_stats[key], dict):
                    combined_stats[key].update(value)
                else:
                    combined_stats[key] = value
        
        return final_content, combined_stats
    
    def get_stats(self) -> dict:
        """Get the current statistics."""
        return self.stats
