# Content Optimizer - Project Structure

This document provides an overview of the Content Optimizer's project structure, modules, and key components to help developers understand and contribute to the project.

## Directory Structure

```
/home/martin-m/content-optimiser/
├── content_helpers/               # Main helpers package
│   ├── __init__.py                # Package initialization and factory methods
│   ├── base_helper.py             # Abstract base class for all helpers
│   ├── code_helper.py             # Code file optimization helper
│   ├── docs_helper.py             # Documentation optimization helper
│   ├── email_helper.py            # Email content optimization helper
│   ├── markdown_helper.py         # Markdown/HTML optimization helper
│   ├── notion_helper.py           # Notion export optimization helper
│   └── unified_optimizer.py       # Content auto-detection and unified optimization
├── docs/                          # Documentation assets
│   └── images/                    # Images for documentation
│       └── demo.gif               # Demo image for README
├── tests/                         # Test suite (future development)
├── optimize.py                    # Main script - entry point for the application
├── generate_training_data.py      # Script for generating LLM training data
├── optimization_rules.py          # Pattern definitions and optimization rules
├── optimize-quick.sh              # Bash wrapper for common optimization scenarios
├── fix-permissions.sh             # Script to set proper executable permissions
├── requirements.txt               # Project dependencies
├── PROJECT_STRUCTURE.md           # This file - project structure documentation
├── README.md                      # Project overview and quick start guide
├── USAGE_GUIDE.md                # Detailed usage guide with examples
└── HELPER_CONFIG.md              # Helper configuration documentation
```

## Core Files

### Main Components
- `optimize.py` - Main entry point and CLI interface
- `generate_training_data.py` - LLM training data generation
- `optimization_rules.py` - Regular expression patterns for optimization
- `requirements.txt` - Project dependencies
- `optimize-quick.sh` - Simplified command interface
- Documentation files (README.md, etc.)

### Utility Scripts
- `fix-permissions.sh` - Sets proper executable permissions
- `fix-specific-form.sh` - Form-specific cleanup utilities
- `fix-forms.sh` - General form cleanup utilities
- `fix-optimization.sh` - Optimization-specific utilities
- `fix-duplicate-content.sh` - Duplicate content handling

## Core Modules

### Main Script (optimize.py)

The entry point for the application, handling:
- Command line argument parsing
- Input validation and processing
- Directory scanning and file filtering
- Content optimization coordination
- Output generation and reporting

Key functions:
- `main()`: Entry point and argument processing
- `process_with_content_helpers()`: Optimization coordination
- `scan_directory()`: Directory traversal with filtering
- `generate_report()`: Detailed report generation

### Content Helpers Package

The `content_helpers` package contains specialized modules for different content types:

#### Base Helper (base_helper.py)

Abstract base class defining the interface all helpers must implement:

```python
class ContentHelperBase:
    def detect_content_type(self, file_path, content=None) -> float:
        """Determine confidence this is the right helper (0.0-1.0)"""
        
    def preprocess_content(self, content, file_path=None) -> dict:
        """Prepare content for optimization"""
        
    def optimize_content(self, content_data, file_path=None) -> tuple:
        """Apply content-specific optimizations"""
        
    def postprocess_content(self, content, file_path=None) -> str:
        """Apply final processing"""
```

#### Unified Optimizer (unified_optimizer.py)

Handles content detection and routing:
- `detect_content_type()`: Determines best helper for content
- `optimize_file()`: Processes with best helper
- `optimize_directory()`: Processes entire directories
- `get_stats()`: Retrieves optimization statistics

#### Code Helper (code_helper.py)

Specialized for source code optimization:
- Automatic language detection using file extensions and content analysis
- Language-specific optimization rules
- Preservation of code structure and important comments
- Smart handling of imports and dependencies
- Support for multiple programming languages

#### Documentation Helper (docs_helper.py)

Optimized for documentation content:
- Markdown formatting preservation
- Header and structure maintenance
- Table and list handling
- Navigation element removal
- Version information preservation

#### Email Helper (email_helper.py)

Specialized for email content:
- Email thread processing
- Header and signature cleanup
- Quote level management
- Attachment reference handling
- Thread visualization preservation

#### Markdown Helper (markdown_helper.py)

Enhanced for Markdown/HTML:
- Mixed content handling
- HTML tag processing
- Image and link management
- YAML frontmatter handling
- Table and list preservation

#### Notion Helper (notion_helper.py)

Specialized for Notion exports:
- Notion ID handling
- Property block conversion
- Block element processing
- Export-specific formatting
- Reference preservation

## Flow of Execution

1. **Command Processing**:
   - Parse command line arguments
   - Validate inputs and paths
   - Set up configuration

2. **Directory Scanning**:
   - Scan for matching files
   - Apply ignore patterns
   - Filter by extensions
   - Respect .gitignore rules

3. **Content Processing**:
   - If auto mode:
     1. Detect content type for each file
     2. Route to appropriate helper
   - If specific mode:
     1. Use designated helper for all files
   
4. **Helper Processing Pipeline**:
   - Preprocess: Prepare content and extract metadata
   - Optimize: Apply content-specific rules
   - Postprocess: Final cleanup and formatting

5. **Output Generation**:
   - Write optimized content
   - Generate directory structure
   - Create detailed report

6. **Statistics and Reporting**:
   - Calculate token/character reductions
   - Compile optimization statistics
   - Generate helper-specific metrics
   - Create markdown report

## Helper Design Pattern

Uses the Template Method pattern:
1. `ContentHelperBase` defines the processing workflow
2. Each helper implements specialized behavior
3. Factory method returns appropriate helper
4. Unified optimizer coordinates helper selection

Benefits:
- Consistent interface across helpers
- Specialized processing per content type
- Easy addition of new helpers
- Centralized optimization coordination

## Adding a New Helper

1. Create new file in `content_helpers/`
2. Extend `ContentHelperBase`
3. Implement required methods
4. Add detection patterns
5. Register in `__init__.py`
6. Update documentation

Example:
```python
from .base_helper import ContentHelperBase

class NewHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="NewHelper", **kwargs)
        
    def detect_content_type(self, file_path, content=None):
        # Return confidence score 0.0-1.0
        
    def preprocess_content(self, content, file_path=None):
        # Prepare content
        
    def optimize_content(self, content, file_path=None):
        # Apply optimizations
        
    def postprocess_content(self, content, file_path=None):
        # Final processing
```

## Future Development

1. **Test Suite**:
   - Unit tests for helpers
   - Integration tests
   - Performance benchmarks

2. **Web Interface**:
   - Browser-based optimization
   - Real-time preview
   - Configuration UI

3. **Enhanced Helpers**:
   - PDF content processing
   - Image caption handling
   - Code documentation
   - API documentation

4. **Optimization Profiles**:
   - Use case specific settings
   - Custom rule sets
   - Profile sharing

5. **Plugin System**:
   - Dynamic rule loading
   - Custom helper plugins
   - Extension framework

6. **Language Support**:
   - Multi-language processing
   - Character set handling
   - RTL text support