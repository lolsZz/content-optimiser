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
├── generate_training_data.py      # Script for generating LLM training data from optimized content
├── optimize-quick.sh              # Bash wrapper for common optimization scenarios
├── fix-permissions.sh             # Script to set proper executable permissions
├── optimization_rules.py          # Pattern definitions and optimization rules
├── PROJECT_STRUCTURE.md           # This file - project structure documentation
├── README.md                      # Project overview and quick start guide
├── USAGE_GUIDE.md                 # Detailed usage guide with examples
└── requirements.txt               # Project dependencies
```

## Core Files

- `optimize.py` - Main script for content optimization
- `generate_training_data.py` - Script for generating LLM training data from optimized content
- `optimization_rules.py` - Defines patterns and rules for content optimization
- `requirements.txt` - Python dependencies
- `optimize-quick.sh` - Bash script for quick usage
- `fix-permissions.sh` - Script to set proper executable permissions
- `README.md` - Project documentation

## Core Modules

### Main Script (optimize.py)

The main script serves as the entry point for the application, handling:

- Command line argument parsing
- Input validation and processing
- Directory scanning and file filtering
- Content optimization coordination
- Output generation
- Reporting

Key functions:
- `main()`: Entry point, parses arguments and initiates processing
- `process_with_content_helpers()`: Coordinates the optimization process
- `scan_directory()`: Handles directory traversal with filtering
- `generate_report()`: Creates detailed markdown reports

### Quick Wrapper (optimize-quick.sh)

A Bash script that provides a simplified interface for common operations. It:
- Parses simple commands and maps them to optimize.py flags
- Provides helpful usage information
- Ensures scripts have proper execute permissions

### Content Helpers Package

The `content_helpers` package provides specialized modules for different types of content:

#### Factory Functions (__init__.py)

- `get_content_helper(content_type, **kwargs)`: Returns the appropriate helper instance
- `get_unified_optimizer(default_mode="docs", **kwargs)`: Returns a unified optimizer

#### Base Helper (base_helper.py)

`ContentHelperBase` is an abstract base class that defines the interface all helpers must implement:

- `detect_content_type(file_path, content=None)`: Determine confidence this is the right helper
- `preprocess_content(content, file_path=None)`: Prepare content for optimization
- `optimize_content(content, file_path=None)`: Apply content-specific optimizations
- `postprocess_content(content, file_path=None)`: Apply final processing
- `process_file(file_path, content=None)`: Complete processing pipeline

#### Unified Optimizer (unified_optimizer.py)

`UnifiedOptimizer` provides content auto-detection and routing:

- `detect_content_type(file_path, content=None)`: Determine best helper for content
- `optimize_file(file_path, content=None, force_mode=None)`: Process with best helper
- `optimize_directory(directory_path, force_mode=None)`: Process entire directories

#### Specialized Helpers

Each specialized helper inherits from `ContentHelperBase` and implements content-specific behavior:

1. **Code Helper (code_helper.py)**
   - Detects and optimizes source code files
   - Identifies programming languages
   - Preserves code structure while removing noise

2. **Documentation Helper (docs_helper.py)**
   - Optimizes documentation content
   - Handles markdown headers, code blocks, and tables
   - Removes navigation elements while preserving structure

3. **Email Helper (email_helper.py)**
   - Processes email content and threads
   - Cleans up headers, signatures, and disclaimers
   - Handles quoted replies with configurable depth

4. **Markdown Helper (markdown_helper.py)**
   - Optimizes Markdown and HTML content
   - Cleans unnecessary HTML while preserving structure
   - Handles images, links, and formatting

5. **Notion Helper (notion_helper.py)**
   - Processes Notion.so exports
   - Handles Notion IDs and specific formatting
   - Converts properties blocks to frontmatter

### Optimization Rules (optimization_rules.py)

Defines regular expression patterns for identifying and removing common noise elements:

- Website chrome (headers, footers, navigation)
- Contact forms and subscription boxes
- Tracking pixels and non-essential metadata
- Policy sections and disclaimers
- Redundant formatting and structure

## Flow of Execution

1. **User Invocation**: User runs `optimize.py` or `optimize-quick.sh` with arguments
2. **Argument Parsing**: Script parses arguments to determine mode and options
3. **Directory Scanning**: If processing a directory, files are scanned and filtered
4. **Helper Selection**:
   - If auto mode, content is analyzed to determine the appropriate helper
   - Otherwise, the specified helper is used
5. **Content Processing**:
   - **Preprocessing**: Content is prepared and metadata extracted
   - **Optimization**: Content-specific rules are applied
   - **Postprocessing**: Final cleanup and formatting
6. **Output Generation**: Optimized content is written to the output file
7. **Report Generation**: Detailed statistics and analysis are compiled into a report

## Helper Design Pattern

The `ContentHelperBase` defines a template method pattern where:
1. `process_file()` is the template method that defines the workflow
2. Subclasses override the abstract methods to provide specialized behavior
3. The factory method `get_content_helper()` returns the appropriate concrete implementation

This design allows for:
- Consistent interface across all helpers
- Specialized logic for different content types
- Easy addition of new helpers

## Adding a New Helper

To create a new specialized helper:

1. Create a new file in `content_helpers/` (e.g., `my_helper.py`)
2. Define a class that extends `ContentHelperBase`
3. Implement all required abstract methods
4. Add detection patterns specific to your content type
5. Register the helper in `content_helpers/__init__.py` 
6. Update documentation as needed

Example:
```python
# content_helpers/my_helper.py
from .base_helper import ContentHelperBase

class MyHelper(ContentHelperBase):
    def __init__(self, **kwargs):
        super().__init__(name="MyHelper", **kwargs)
        # Initialize settings and stats
        
    def detect_content_type(self, file_path, content=None):
        # Return confidence score 0.0-1.0
        
    def preprocess_content(self, content, file_path=None):
        # Prepare content and extract metadata
        
    def optimize_content(self, content, file_path=None):
        # Apply content-specific optimizations
        
    def postprocess_content(self, content, file_path=None):
        # Final formatting and cleanup
```

Then register in `__init__.py`:
```python
from .my_helper import MyHelper

def get_content_helper(content_type, **kwargs):
    helpers = {
        # ... existing helpers ...
        'my_type': MyHelper,
    }
    # ... rest of function ...
```

## Future Development

Areas for future enhancement:

1. **Test Suite**: Develop comprehensive unit and integration tests
2. **Web Interface**: Create a web UI for easier file processing
3. **Additional Helpers**: Support for more specialized content types
4. **Optimization Profiles**: Predefined optimization settings for different use cases
5. **Plugin System**: Allow for dynamic loading of additional optimization rules
6. **Language Support**: Improve handling of non-English content