# Content Optimizer

![Version](https://img.shields.io/badge/version-2.0.0-blue) 
![Python](https://img.shields.io/badge/python-3.6%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A Python tool for cleaning and optimizing text content for Large Language Model (LLM) consumption by removing boilerplate, website chrome, and irrelevant elements.

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/content-optimiser/main/docs/images/demo.gif" alt="Content Optimizer Demo" width="700">
</p>

## Overview

Content Optimizer intelligently detects and processes different types of content, applying specialized optimizations to improve signal-to-noise ratio for LLM consumption. It automatically removes common noise patterns from:

- Web-scraped content and documentation
- Source code repositories
- Notion.so exports
- Email content and threads
- Markdown and HTML content

The tool can greatly reduce token usage and improve context quality by removing unnecessary elements while preserving important information.

## ✨ Key Features

- **Smart Content Detection**: Automatically detects content type and applies appropriate optimizations
- **Multiple Optimization Modes**:
  - `auto`: Intelligently detect and process each file with the appropriate helper
  - `docs`: Optimized for documentation/web content
  - `code`: Conservative optimization for source code repositories
  - `notion`: Specialized handling for Notion.so exports
  - `email`: Optimized for email content and threads
  - `markdown`: Enhanced for Markdown and HTML content
- **Versatile Processing Options**:
  - Process entire directories of files with custom filtering
  - Process individual files with specific optimizations
  - Handle Notion exports with specialized formatting
  - Process email threads while maintaining readability
- **Advanced Features**:
  - Policy page filtering (privacy policies, terms of service)
  - Detailed markdown reports with optimization statistics
  - Token counting with OpenAI's tiktoken library
  - Respect .gitignore patterns during directory scans
  - Visual progress tracking during processing
  - Colorized command-line interface

## 🚀 Quick Start

The simplest way to get started is with the `optimize-quick.sh` script:

```bash
# Auto-detect content types (recommended)
./optimize-quick.sh auto ./mixed-content

# For documentation/web content
./optimize-quick.sh docs ./my-documentation-directory

# For source code repositories
./optimize-quick.sh code ./my-code-repository

# For Notion.so exports
./optimize-quick.sh notion ./my-notion-export

# For email content
./optimize-quick.sh email ./my-email-archive
```

Or use the Python script directly with the quick options:

```bash
# Auto-detection mode (recommended)
python optimize.py -a ./mixed-content

# Quick docs mode
python optimize.py -q ./my-documentation-directory

# Quick Notion export mode
python optimize.py -n ./my-notion-export
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
  - `mail-parser`: For structured parsing of email content

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

### Process Documentation

```bash
# Process with documentation-specific optimizations
python optimize.py -d ./my-documentation -m docs
```

### Process Source Code

```bash
# Conservative optimization preserving code structure
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

### Filter Files by Type

```bash
# Process only specific file types
python optimize.py -d ./mixed-content --extensions .md,.txt,.rst
```

### Custom Ignore Patterns

```bash
# Ignore specific file patterns
python optimize.py -d ./project --ignore "test/,*.test.js,temp/,*.bak"
```

### Include Policy Pages in Output

```bash
# Process all files including policy pages
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

## 📖 Documentation

For more details, see:
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Comprehensive guide with examples and configuration options
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Overview of project structure for developers

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
