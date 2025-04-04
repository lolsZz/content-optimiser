"""
Unified interface for content optimization using specialized helpers
"""

import os
import time
from collections import defaultdict
from pathlib import Path

from . import get_content_helper
from .base_helper import ContentHelperBase

class UnifiedOptimizer:
    """
    Provides a unified interface for optimizing content using specialized helpers.
    Handles content type detection and dispatches to the appropriate helper.
    """
    
    def __init__(self, default_mode="docs", **kwargs):
        """
        Initialize the unified optimizer.
        
        Args:
            default_mode: Default mode to use if auto-detection fails
            **kwargs: Additional parameters passed to content helpers
        """
        self.default_mode = default_mode
        self.config = kwargs
        self.helpers = {}
        self.stats = {
            "files_processed": 0,
            "auto_detected": 0,
            "detection_failures": 0,
            "processing_time": 0,
            "detected_types": defaultdict(int),
            "errors": []
        }
    
    def _get_helper(self, content_type):
        """Get or create a helper instance for the specified content type"""
        if content_type not in self.helpers:
            self.helpers[content_type] = get_content_helper(content_type, **self.config)
        return self.helpers[content_type]
    
    def detect_content_type(self, file_path, content=None):
        """
        Determine the most appropriate content type for a file.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file (to avoid re-reading)
            
        Returns:
            tuple: (content_type, confidence)
        """
        # Check if content needs to be loaded
        if content is None and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(8000)  # Read a reasonable sample
            except Exception as e:
                self.stats["errors"].append(f"Error reading {file_path}: {str(e)}")
                return self.default_mode, 0.0
        
        # Get confidence scores from all helpers
        scores = {}
        for content_type in ['notion', 'email', 'code', 'docs', 'markdown']:
            try:
                helper = self._get_helper(content_type)
                scores[content_type] = helper.detect_content_type(file_path, content)
            except Exception as e:
                self.stats["errors"].append(f"Error in {content_type} detection for {file_path}: {str(e)}")
                scores[content_type] = 0.0
        
        # Find the best match
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # Fall back to default if confidence is too low
        if confidence < 0.3:
            return self.default_mode, confidence
        
        return best_type, confidence
    
    def optimize_file(self, file_path, content=None, force_mode=None):
        """
        Optimize a single file using the appropriate content helper.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file (to avoid re-reading)
            force_mode: Force a specific mode instead of auto-detecting
            
        Returns:
            tuple: (optimized_content, stats)
        """
        start_time = time.time()
        result_stats = {}
        
        # Return empty result for None or non-existent file paths
        if file_path is None or not os.path.exists(file_path):
            error_msg = f"Invalid file path: {file_path}"
            self.stats["errors"].append(error_msg)
            return "", {"error": error_msg}
        
        # Read content if not provided
        if content is None and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                self.stats["errors"].append(f"Error reading {file_path}: {str(e)}")
                return None, {"error": str(e)}
        
        # Store original content length for comparison
        original_length = len(content) if content else 0
        
        # Detect content type if not forced
        if force_mode:
            content_type = force_mode
            result_stats["detection"] = {"mode": "forced", "type": content_type}
        else:
            content_type, confidence = self.detect_content_type(file_path, content)
            self.stats["detected_types"][content_type] += 1
            self.stats["auto_detected"] += 1
            result_stats["detection"] = {"mode": "auto", "type": content_type, "confidence": confidence}
        
        # Handle empty content case
        if not content:
            self.stats["files_processed"] += 1
            return "", {"empty_file": 1}
        
        # Get the appropriate helper and process
        try:
            helper = self._get_helper(content_type)
            optimized_content, opt_stats = helper.process_file(file_path, content)
            
            # Update statistics
            self.stats["files_processed"] += 1
            processing_time = time.time() - start_time
            self.stats["processing_time"] += processing_time
            
            # Check for size increase
            if "size_increased" in opt_stats and opt_stats.get("reverted_to_original", False):
                self.stats["size_increases"] = self.stats.get("size_increases", 0) + 1
                result_stats["size_increased"] = opt_stats["size_increased"]
                result_stats["reverted_to_original"] = True
            
            # Combine stats
            result_stats.update(opt_stats)
            result_stats["processing_time"] = processing_time
            
            # Ensure we never return None
            if optimized_content is None:
                optimized_content = ""
                result_stats["error"] = "Helper returned None content"
                
            # Final size check - if optimization increased size substantially, revert to original
            optimized_length = len(optimized_content) if optimized_content else 0
            if optimized_length > original_length * 1.05:  # More than 5% size increase
                self.stats["reverted_optimizations"] = self.stats.get("reverted_optimizations", 0) + 1
                result_stats["size_increased"] = optimized_length - original_length
                result_stats["reverted_to_original"] = True
                return content, result_stats
                
            return optimized_content, result_stats
        except Exception as e:
            error_msg = f"Error processing {file_path} with {content_type} helper: {str(e)}"
            self.stats["errors"].append(error_msg)
            self.stats["detection_failures"] += 1
            # Return original content on error rather than None
            return content or "", {"error": error_msg}
    
    def optimize_directory(self, directory_path, force_mode=None, extensions=None, ignore_patterns=None):
        """
        Optimize all files in a directory.
        
        Args:
            directory_path: Path to the directory
            force_mode: Force a specific mode instead of auto-detecting
            extensions: Set of file extensions to include
            ignore_patterns: List of glob patterns to ignore
            
        Returns:
            tuple: (optimized_files, stats)
        """
        optimized_files = {}
        start_time = time.time()
        
        for root, _, files in os.walk(directory_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Skip files based on extension if specified
                if extensions and not any(file_path.lower().endswith(ext) for ext in extensions):
                    continue
                
                # Process the file
                try:
                    rel_path = os.path.relpath(file_path, directory_path)
                    optimized, file_stats = self.optimize_file(file_path, force_mode=force_mode)
                    optimized_files[rel_path] = optimized
                except Exception as e:
                    self.stats["errors"].append(f"Error processing {file_path}: {str(e)}")
        
        self.stats["total_time"] = time.time() - start_time
        return optimized_files, self.stats
    
    def get_stats(self):
        """Get combined statistics from all helpers and this optimizer"""
        combined_stats = dict(self.stats)
        helper_stats = {}
        
        for content_type, helper in self.helpers.items():
            helper_stats[content_type] = helper.get_stats()
        
        combined_stats["helper_stats"] = helper_stats
        return combined_stats
