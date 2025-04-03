# Content Optimizer

![Version](https://img.shields.io/badge/version-2.0.0-blue) 
![Python](https://img.shields.io/badge/python-3.6%2B-green)

A Python tool for cleaning and optimizing text content for Large Language Model (LLM) consumption by removing boilerplate, website chrome, and irrelevant elements.

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/content-optimiser/main/docs/images/demo.gif" alt="Content Optimizer Demo" width="700">
</p>

## Overview

Content Optimizer automatically removes common noise patterns from:
- Web-scraped content
- Documentation repositories
- Source code repositories 
- Repomix-format files
- Notion.so exports
- Email content and threads
- Markdown and HTML content

## ✨ Features

- **Smart Content Detection**: Automatically detects content type and applies appropriate optimizations
- **Multiple Optimization Modes**:
  - `docs`: Optimized for documentation/web content
  - `code`: Conservative optimization for source code repositories
  - `notion`: Specialized handling for Notion.so exports
  - `email`: Optimized for email content and threads
  - `markdown`: Enhanced for Markdown and HTML content
  - `auto`: Automatically detect content type for each file
- **Directory Scanning**: Process entire directories of files with custom filtering
- **Repomix Support**: Process structured files produced by Repomix
- **Notion Export Handling**: Clean Notion content IDs and format for improved readability
- **Email Processing**: Handle email threads, signatures, and quotes
- **Code-aware Optimization**: Language-specific handling of source code
- **Policy Filter**: Option to exclude policy pages (privacy, terms, etc.)
- **Detailed Reports**: Get comprehensive markdown reports on the optimization process
- **Token Counting**: Calculate token reduction (with optional tiktoken library)
- **Gitignore Support**: Respect .gitignore files during directory scans
- **Progress Tracking**: Visual progress bars during processing
- **Interactive CLI**: Colorized, user-friendly command-line interface
- **Quick Start**: Simplified interface for common use cases

## 🚀 Quick Start

The simplest way to get started is with the `optimize-quick.sh` script:

```bash
# For documentation/web content
./optimize-quick.sh docs ./my-documentation-directory

# For source code repositories
./optimize-quick.sh code ./my-code-repository

# For Notion.so exports
./optimize-quick.sh notion ./my-notion-export

# For email content
./optimize-quick.sh email ./my-email-archive

# For auto-detection (recommended)
./optimize-quick.sh auto ./mixed-content
```

Or use the Python script directly with the quick options:

```bash
# Quick docs mode
python optimize.py -q ./my-documentation-directory

# Quick Notion export mode
python optimize.py -n ./my-notion-export

# Auto-detection mode (recommended)
python optimize.py -a ./mixed-content
```

## 📦 Installation

### Prerequisites

- Python 3.6+
- Optional dependencies:
  - `tqdm`: For visual progress bars (highly recommended)
  - `tiktoken`: For accurate token counting (OpenAI models)
  - `gitignore-parser`: For respecting .gitignore rules in directory scans
  - `pygments`: For better code detection and language identification
  - `beautifulsoup4`: For better HTML cleaning in Markdown mode

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/content-optimiser.git
cd content-optimiser

# Optional but recommended: Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📚 Usage Examples

### Auto-detect Content Types (Recommended)

```bash
# Automatically detect and apply the best optimizer for each file
python optimize.py -a ./mixed-content
```

### Process Documentation with Default Settings

```bash
python optimize.py -d ./my-documentation -m docs
```

### Process Source Code

```bash
python optimize.py -d ./source-code-repo -m code
```

### Process a Notion.so Export

```bash
# Process a Notion export with specialized handling
python optimize.py -n ./my-notion-export
```

### Process Email Content

```bash
# Process email files with specialized handling
python optimize.py -d ./email-archives -m email
```

### Process Only Specific File Types

```bash
python optimize.py -d ./mixed-content --extensions .md,.txt,.rst
```

### Process a Directory with Custom Ignores

```bash
python optimize.py -d ./project --ignore "test/,*.test.js,temp/,*.bak"
```

### Include Policy Pages in Output

```bash
python optimize.py -d ./website-scrape --no-policy-filter
```

## 📊 Output

The script generates two files:

1. **Optimized Content File**: Contains the cleaned content with unnecessary elements removed
2. **Markdown Report**: Detailed analysis including:
   - Character and token reduction statistics
   - Breakdown of applied optimizations by category
   - Content type detection results
   - Skipped files and policy pages
   - Warnings encountered during processing

## 📋 Command Line Options

```
usage: optimize.py [-h] (-d INPUT_DIR | -i INPUT_FILE | -q DIR | -n DIR | -a DIR)
                   [-o OUTPUT_FILE] [-m {code,docs,notion,email,markdown,auto}]
                   [--report_file REPORT_FILE] [--extensions EXTENSIONS]
                   [--ignore IGNORE] [--use-gitignore]
                   [--policy-filter | --no-policy-filter]

Optimize text content for LLM consumption by removing noise and boilerplate.

options:
  -h, --help            show this help message and exit
  -d INPUT_DIR, --input_dir INPUT_DIR
                        Path to the root directory of the content to scan.
  -i INPUT_FILE, --input_file INPUT_FILE
                        Path to the input file (e.g., a Repomix file).
  -q DIR, --quick DIR   Quick optimization of a directory with sensible defaults
                        (equivalent to: -d DIR -m docs)
  -n DIR, --notion DIR  Process a Notion.so export directory with optimal settings
                        for Notion content (equivalent to: -d DIR -m notion)
  -a DIR, --auto DIR    Auto-detect content types and apply appropriate optimizations
                        (equivalent to: -d DIR -m auto)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path for the optimized output file. If omitted, generated
                        automatically based on input name and timestamp.
                        (default: None)
  -m {code,docs,notion,email,markdown,auto}, --mode {code,docs,notion,email,markdown,auto}
                        Optimization mode. Use 'auto' to automatically detect and
                        apply the best optimization for each file type.
                        (default: docs)
  --report_file REPORT_FILE
                        Path for the optimization report file (Markdown). If
                        omitted, generated based on output file name.
                        (default: None)

Directory Scanning Options (used with -d/--input_dir):
  --extensions EXTENSIONS
                        Comma-separated list of file extensions to include (e.g.,
                        '.py,.md,.txt'). Case-insensitive.
  --ignore IGNORE       Comma-separated list of glob patterns (like .gitignore
                        syntax) for files/directories to ignore.
  --use-gitignore       Attempt to read and respect rules from a .gitignore file
                        in the input directory.
  --policy-filter       Enable filtering of potential policy pages (default).
  --no-policy-filter    Disable filtering of policy pages (process all files).
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
