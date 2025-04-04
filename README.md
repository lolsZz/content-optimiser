# Content Optimizer

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)
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
- **Language-Aware Code Processing**:
  - Automatic programming language detection
  - Language-specific optimization rules
  - Preserves important code structures and comments
  - Smart handling of imports and dependencies
- **Advanced Optimization Features**:
  - Policy page filtering (privacy policies, terms of service)
  - Detailed markdown reports with optimization statistics
  - Token counting with OpenAI's tiktoken library
  - Respect .gitignore patterns during directory scans
  - Visual progress tracking during processing
  - Colorized command-line interface
- **Content-Type Specific Processing**:
  - Email threads and forwarded messages
  - Notion export-specific formatting
  - Documentation structure preservation
  - Code repository optimization
  - Mixed content handling
- **NEW: LLM Training Data Generation**:
  - Convert optimized content into various LLM training formats
  - Generate instruction tuning data, conversational data, and more
  - Filter examples by token count for targeted training
  - Multiple output formats: JSONL, CSV, Parquet, Hugging Face datasets

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

# Generate training data from an optimized file
./optimize-quick.sh train ./optimized-content.md
```

Or use the Python script directly with the quick options:

```bash
# Auto-detection mode (recommended)
python optimize.py -a ./mixed-content

# Quick docs mode
python optimize.py -q ./my-documentation-directory

# Quick Notion export mode
python optimize.py -n ./my-notion-export

# Generate LLM training data
python generate_training_data.py -i ./optimized-content.md -f instruction
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- Optional dependencies:
  - `tqdm`: For visual progress bars (highly recommended)
  - `tiktoken`: For accurate token counting (OpenAI models)
  - `gitignore-parser`: For respecting .gitignore rules in directory scans
  - `pygments`: For better code detection and language identification
  - `beautifulsoup4`: For better HTML cleaning in Markdown mode
  - `mail-parser`: For structured parsing of email content
  - `pandas`: For Parquet export of training data
  - `datasets`: For Hugging Face dataset export

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/content-optimiser.git
cd content-optimiser

# Set up a virtual environment (required)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
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

### Generate LLM Training Data

```bash
# Create instruction tuning data from an optimized file
python generate_training_data.py -i ./optimized-content.md -f instruction

# Create conversational data with custom token limits
python generate_training_data.py -i ./optimized-content.md -f conversation --min_tokens 100 --max_tokens 2048

# Process multiple files with a glob pattern
python generate_training_data.py -i "./optimized-*.md" -f general -o ./training-data
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
   - Language detection results for code files
   - Skipped files and policy pages
   - Warnings encountered during processing

## 📖 Documentation

For more details, see:
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Comprehensive guide with examples and configuration options
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Overview of project structure for developers
- [HELPER_CONFIG.md](HELPER_CONFIG.md) - Detailed configuration options for content helpers

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
