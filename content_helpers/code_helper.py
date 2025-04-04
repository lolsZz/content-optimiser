"""
Helper module for processing source code files
"""

import re
import os
from pathlib import Path
from collections import defaultdict
import sys

try:
    import pygments
    from pygments.lexers import get_lexer_for_filename, guess_lexer
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

from .base_helper import ContentHelperBase

# Code-specific patterns for removing/optimizing
CODE_BOILERPLATE_HEADER = re.compile(r'^/\*[\s\*]*(?:Copyright|License|Author|Created by).*?\*/\s*\n', re.DOTALL)
CODE_BOILERPLATE_COMMENT = re.compile(r'^(?://|#)\s*(?:Copyright|License|Author|Created by).*?\n')
CODE_DOCSTRING_COPYRIGHT = re.compile(r'"""[\s\*]*(?:Copyright|License|Author|Created by).*?"""\s*\n', re.DOTALL)
CODE_LOG_STATEMENT = re.compile(r'(?:console\.log|print|System\.out\.println|printf|cout|fprintf|log\.(?:debug|info|warning|error)).*?\).*?\n')
CODE_COMMENTED_CODE_BLOCK = re.compile(r'(?:^|\n)(?:\/\/|#).*(?:TODO|FIXME|XXX|HACK):?\s+.*(?:\n(?:\/\/|#).*)*', re.MULTILINE)

# Language-specific code patterns
CODE_IMPORT_GROUPS = {
    'python': re.compile(r'(?:^import\s+[^;]+$|^from\s+[^;]+$)(?:\n(?:import\s+[^;]+$|from\s+[^;]+$))*', re.MULTILINE),
    'javascript': re.compile(r'(?:^import\s+[^;]+;|^const\s+\w+\s*=\s*require\([^)]+\);)(?:\n(?:^import\s+[^;]+;|^const\s+\w+\s*=\s*require\([^)]+\);))*', re.MULTILINE),
}

# Extension to language mapping
EXTENSION_TO_LANGUAGE = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.cs': 'csharp',
    '.cpp': 'cpp',
    '.c': 'c',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
}

class CodeHelper(ContentHelperBase):
    """
    Helper for processing source code files
    """
    
    def __init__(self, **kwargs):
        """Initialize the code helper with optional config"""
        super().__init__(name="Code", **kwargs)
        
        # Configure code-specific optimization settings
        self.remove_boilerplate = kwargs.get('remove_boilerplate', True)
        self.remove_logs = kwargs.get('remove_logs', False)  # Default to False for safety
        self.preserve_todos = kwargs.get('preserve_todos', True)
        self.preserve_imports = kwargs.get('preserve_imports', True)
        
        # Code-specific statistics
        self.stats["helper_specific_data"]["boilerplate_removed"] = 0
        self.stats["helper_specific_data"]["logs_removed"] = 0
        self.stats["helper_specific_data"]["detected_languages"] = defaultdict(int)
    
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file contains source code.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is source code
        """
        confidence = 0.0
        
        # Check file extension first
        file_ext = Path(file_path).suffix.lower()
        if file_ext in EXTENSION_TO_LANGUAGE:
            confidence += 0.8
            return min(confidence, 1.0)  # Strong indicator
        
        # If content was not provided, read a sample
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)  # Read first 4KB for detection
            except:
                return 0.0  # Cannot read file
        
        # Try to detect the language using Pygments if available
        if PYGMENTS_AVAILABLE:
            try:
                # Try to guess the lexer based on content
                lexer = guess_lexer(content)
                if lexer:
                    # Certain lexers strongly suggest code content
                    code_lexers = ['Python', 'JavaScript', 'Java', 'C', 'C++', 'Go', 'Rust', 'Ruby', 'PHP']
                    if any(lang in lexer.name for lang in code_lexers):
                        confidence += 0.7
                    else:
                        confidence += 0.3
            except ClassNotFound:
                pass  # If lexer detection fails, continue with other methods
        
        # Check for common code patterns
        
        # Look for import/include statements
        if re.search(r'^(?:import|from|#include|using|require|package)\s+', content, re.MULTILINE):
            confidence += 0.4
        
        # Check for function/method definitions
        if re.search(r'(?:function|def|class|interface|struct|module)\s+\w+', content):
            confidence += 0.5
        
        # Check for variable assignments with common programming syntax
        if re.search(r'(?:var|let|const|int|float|double|string|boolean)\s+\w+\s*=', content):
            confidence += 0.3
        
        # Check for common code constructs like loops and conditionals
        if re.search(r'(?:if|for|while|switch|case)\s*\(', content):
            confidence += 0.3
        
        # Check for common comment patterns
        if re.search(r'(?://|#|/\*|\*/).*?(?:TODO|FIXME|HACK|NOTE)', content):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _detect_language(self, file_path, content):
        """
        Detect the programming language of the file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            str: Detected language or None if unknown
        """
        # First check extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext in EXTENSION_TO_LANGUAGE:
            lang = EXTENSION_TO_LANGUAGE[file_ext]
            self.stats["helper_specific_data"]["detected_languages"][lang] += 1
            return lang
        
        # Try using Pygments if available
        if PYGMENTS_AVAILABLE:
            try:
                lexer = guess_lexer(content)
                lang_name = lexer.name.lower()
                
                # Map Pygments lexer names to our simpler language names
                mappings = {
                    'python': 'python',
                    'javascript': 'javascript',
                    'typescript': 'typescript',
                    'java': 'java',
                    'c#': 'csharp',
                    'c++': 'cpp',
                    'c': 'c',
                    'go': 'go',
                    'rust': 'rust',
                    'ruby': 'ruby',
                    'php': 'php',
                    'swift': 'swift',
                    'kotlin': 'kotlin',
                    'scala': 'scala',
                }
                
                for key, value in mappings.items():
                    if key in lang_name:
                        self.stats["helper_specific_data"]["detected_languages"][value] += 1
                        return value
            except Exception as e:
                logging.exception("Include relevant information about the exception here", e, stack_info=True, exc_info=True)  # import logging
        
        # Fall back to some basic content pattern matching
        if '#!/usr/bin/env python' in content or 'def ' in content and ':' in content:
            self.stats["helper_specific_data"]["detected_languages"]["python"] += 1
            return 'python'
        elif 'function ' in content and '{' in content:
            if 'export ' in content or 'import ' in content and 'from ' in content:
                self.stats["helper_specific_data"]["detected_languages"]["typescript"] += 1
                return 'typescript'
            else:
                self.stats["helper_specific_data"]["detected_languages"]["javascript"] += 1
                return 'javascript'
        
        # Unknown language
        self.stats["helper_specific_data"]["detected_languages"]["unknown"] += 1
        return None
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare code content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            dict: Preprocessed content with metadata
        """
        if not content:
            return {'content': '', 'language': None}
        
        # Detect the language
        language = self._detect_language(file_path, content)
        
        # Return content with detected language
        return {
            'content': content,
            'language': language,
            'file_path': file_path
        }
    
    def optimize_content(self, content_data, file_path=None):
        """
        Apply code-specific optimizations.
        
        Args:
            content_data: Preprocessed content dictionary
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        if not isinstance(content_data, dict):
            # Handle case where content wasn't preprocessed
            content = content_data
            language = self._detect_language(file_path, content)
        else:
            content = content_data['content']
            language = content_data['language']
            file_path = content_data.get('file_path', file_path)
        
        if not content:
            return content, {}
        
        result = content
        stats = defaultdict(int)
        
        # Remove boilerplate headers if configured
        if self.remove_boilerplate:
            # Try different boilerplate patterns based on language
            new_content, count = CODE_BOILERPLATE_HEADER.subn('', result)
            if count > 0:
                result = new_content
                stats["Code Boilerplate Headers"] = count
                self.stats["helper_specific_data"]["boilerplate_removed"] += count
            
            new_content, count = CODE_BOILERPLATE_COMMENT.subn('', result)
            if count > 0:
                result = new_content
                stats["Code Boilerplate Comments"] = count
                self.stats["helper_specific_data"]["boilerplate_removed"] += count
            
            new_content, count = CODE_DOCSTRING_COPYRIGHT.subn('', result)
            if count > 0:
                result = new_content
                stats["Code Docstring Copyright"] = count
                self.stats["helper_specific_data"]["boilerplate_removed"] += count
        
        # Remove log statements if configured
        if self.remove_logs:
            new_content, count = CODE_LOG_STATEMENT.subn('', result)
            if count > 0:
                result = new_content
                stats["Code Log Statements"] = count
                self.stats["helper_specific_data"]["logs_removed"] += count
        
        # Keep TODOs and other developer notes unless configured otherwise
        if not self.preserve_todos:
            new_content, count = CODE_COMMENTED_CODE_BLOCK.subn('', result)
            if count > 0:
                result = new_content
                stats["Code TODO Comments"] = count
        
        # Apply language-specific optimizations
        if language and language in CODE_IMPORT_GROUPS and not self.preserve_imports:
            # Simplify import groups for readability
            pattern = CODE_IMPORT_GROUPS[language]
            
            def simplify_imports(match):
                imports = match.group(0).strip().split('\n')
                if len(imports) <= 2:  # Keep short import sections unchanged
                    return match.group(0)
                return f"{imports[0]}\n# ... {len(imports)-2} more imports ...\n{imports[-1]}"
            
            new_content, count = pattern.subn(simplify_imports, result)
            if count > 0:
                result = new_content
                stats["Code Import Groups"] = count
        
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
        # For code, we generally want to preserve structure
        # Just ensure proper spacing and trailing newline for git-friendliness
        if not content:
            return content
        
        # Ensure single trailing newline
        result = content.rstrip('\n') + '\n'
        
        return result
