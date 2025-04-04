"""
Base class for all content helpers
"""

import re
import os
from abc import ABC, abstractmethod
from pathlib import Path

class ContentHelperBase(ABC):
    """
    Abstract base class for content helpers.
    
    All specific content type helpers should inherit from this base class
    and implement its abstract methods.
    """
    
    def __init__(self, name="BaseHelper", **kwargs):
        """Initialize helper with name and optional configuration."""
        self.name = name
        
        # Initialize statistics tracking
        self.stats = {
            "files_processed": 0,
            "optimizations_applied": 0,
            "helper_specific_data": {
                "duplicates_removed": 0,
                "duplicate_headings_removed": 0,  # New stat for duplicate headings
                "forms_removed": 0,  # New stat for forms
            }
        }
    
    @abstractmethod
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file contains the specific content type this helper handles.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file (to avoid re-reading)
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is the appropriate content type
        """
        pass
    
    @abstractmethod
    def preprocess_content(self, content, file_path=None):
        """
        Prepare content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Preprocessed content
        """
        pass
    
    @abstractmethod
    def optimize_content(self, content, file_path=None):
        """
        Apply content-specific optimizations.
        
        Args:
            content: String content to optimize
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        pass
    
    @abstractmethod
    def postprocess_content(self, content, file_path=None):
        """
        Apply final processing after optimization.
        
        Args:
            content: String content to postprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Postprocessed content
        """
        pass
    
    def clean_file_path(self, path):
        """
        Clean up a file path for display if needed.
        
        Args:
            path: Original file path
            
        Returns:
            str: Cleaned path
        """
        return path
    
    def get_stats(self):
        """
        Get statistics about processing done by this helper.
        
        Returns:
            dict: Statistics dictionary
        """
        return self.stats
    
    def process_file(self, file_path, content=None):
        """
        Process a single file from start to finish.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file (to avoid re-reading)
            
        Returns:
            tuple: (processed_content, stats)
        """
        # Handle None input
        if file_path is None:
            return "", {"error": "Invalid file path (None)"}
            
        # Read content if not provided
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return "", {"error": f"File read error: {str(e)}"}
        
        # Handle empty content
        if not content:
            return "", {"empty_file": 1}
        
        # Store original content length for comparison
        original_length = len(content)
        
        # Apply the full pipeline
        try:
            preprocessed = self.preprocess_content(content, file_path)
            optimized, opt_stats = self.optimize_content(preprocessed, file_path)
            final = self.postprocess_content(optimized, file_path)
            
            # Update statistics
            self.stats["files_processed"] += 1
            self.stats["optimizations_applied"] += sum(opt_stats.values() if isinstance(opt_stats, dict) else 0)
            
            # Ensure we never return None
            if final is None:
                final = ""
                opt_stats["error"] = "Postprocessing returned None content"
            
            # Check if optimization actually reduced size
            final_length = len(final)
            if final_length > original_length:
                # If optimization increased size, revert to original content
                opt_stats["size_increased"] = final_length - original_length
                opt_stats["reverted_to_original"] = True
                return content, opt_stats
                
            return final, opt_stats
        except Exception as e:
            # Return empty string with error info rather than None
            return "", {"error": f"Processing error: {str(e)}"}
