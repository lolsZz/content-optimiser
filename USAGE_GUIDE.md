# Content Optimizer: Comprehensive Usage Guide

This guide provides detailed instructions and best practices for using the Content Optimizer tool to prepare content for Large Language Model (LLM) consumption.

## Table of Contents

- [Understanding How Content Optimizer Works](#understanding-how-content-optimizer-works)
- [Installation and Setup](#installation-and-setup)
- [Basic Usage Workflows](#basic-usage-workflows)
- [Advanced Configuration](#advanced-configuration)
- [Specialized Content Helpers](#specialized-content-helpers)
- [Helper Configuration Options](#helper-configuration-options)
- [Interpreting Reports](#interpreting-reports)
- [Troubleshooting](#troubleshooting)
- [Use Cases and Examples](#use-cases-and-examples)

## Understanding How Content Optimizer Works

Content Optimizer uses specialized content helpers and regular expression patterns to identify and remove common "noise" elements from text content. These elements typically include:

- Website navigation menus, headers, and footers
- Contact forms and subscription boxes
- Tracking pixels and metadata
- Redundant information and formatting
- Policy content (optional)

The tool now features several specialized modes:

- **auto mode**: Automatically detects content type and applies the best optimizations
- **docs mode**: More aggressive optimization suitable for web content and documentation
- **code mode**: More conservative optimization suitable for source code repositories
- **notion mode**: Specialized handling for Notion.so exports
- **email mode**: Optimized for email content and threads
- **markdown mode**: Focused on cleaning up Markdown and HTML content

The optimization process follows these steps:

1. **Content Detection**: Automatically identify content type if in auto mode
2. **Input Processing**: Read content from a directory or a file
3. **Preprocessing**: Prepare content for specific optimizations 
4. **Optimization**: Apply specialized rules based on content type
5. **Postprocessing**: Apply final clean-up and formatting
6. **Output Generation**: Produce a cleaned file and a detailed report

## Installation and Setup

### Full Setup with Virtual Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/content-optimiser.git
cd content-optimiser

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Install Optional Dependencies

For the best experience, install all optional dependencies:

```bash
pip install tqdm tiktoken gitignore-parser pygments beautifulsoup4 mail-parser
```

### Verifying Your Installation

Run a simple test to verify everything is working:

```bash
python optimize.py -h
```

This should display the help message with all available options.

## Basic Usage Workflows

### Workflow 1: Auto-detection (Recommended)

```bash
# Let the tool automatically detect and optimize content
python optimize.py -a ./mixed-content

# Or use the quick script
./optimize-quick.sh auto ./mixed-content
```

### Workflow 2: Optimizing Documentation for an LLM

```bash
# Basic documentation optimization
python optimize.py -d ./my-docs -m docs

# Using the quick script
./optimize-quick.sh docs ./my-docs
```

### Workflow 3: Processing a Source Code Repository

```bash
# Process source code with less aggressive optimization
python optimize.py -d ./my-code-repo -m code

# Using the quick script
./optimize-quick.sh code ./my-code-repo
```

### Workflow 4: Processing a Notion Export

```bash
# Process a Notion export with specialized handling
python optimize.py -n ./my-notion-export

# Using the quick script
./optimize-quick.sh notion ./my-notion-export
```

### Workflow 5: Processing Email Content

```bash
# Process email files with specialized handling
python optimize.py -d ./email-archives -m email

# Using the quick script
./optimize-quick.sh email ./my-email-archive
```

## Advanced Configuration

### Custom File Selection

Fine-tune which files are processed when scanning directories:

```bash
# Include only specific file types
python optimize.py -d ./content --extensions .md,.txt,.html,.rst

# Ignore specific patterns
python optimize.py -d ./content --ignore "draft/,*-old.md,_archive/,temp/"

# Respect .gitignore rules
python optimize.py -d ./repo --use-gitignore
```

### Policy Page Filtering

By default, the tool filters out potential policy pages (privacy policies, terms of service, etc.) since these are often not needed for LLM training and may contain sensitive information:

```bash
# Explicitly enable policy filtering (default behavior)
python optimize.py -d ./website-content --policy-filter

# Disable policy filtering to include all content
python optimize.py -d ./website-content --no-policy-filter
```

### Output Customization

Control where output files are saved:

```bash
# Specify both output file and report locations
python optimize.py -d ./input -o ./output/clean.md --report_file ./reports/details.md
```

## Specialized Content Helpers

The optimizer now includes specialized helpers for different content types, each with its own optimization logic and capabilities:

### Auto-detection (Recommended)

**Purpose**: Automatically detects the most appropriate content type for each file.

**Key Features**:
- Analyzes each file individually to determine its content type
- Applies specialized optimizations based on detected type
- Provides detailed report on detected content types and optimizations
- Handles mixed content repositories effectively

**Usage**:
```bash
python optimize.py -a ./mixed-content
```

### Notion Helper

**Purpose**: Handles Notion.so exports with embedded content IDs.

**Key Features**:
- Cleans Notion IDs from filenames for readability while preserving them in a reference table
- Converts Notion properties blocks to standard YAML frontmatter
- Handles Notion-specific artifacts and formatting
- Processes Notion callouts and toggle blocks

**Usage**:
```bash
python optimize.py -n ./my-notion-export
```

### Email Helper

**Purpose**: Processes email content and threads.

**Key Features**:
- Parses .eml files and other email content
- Cleans up email headers, signatures, and disclaimers
- Handles quoted replies with configurable depth retention
- Processes email footers and forwarded messages

**Usage**:
```bash
python optimize.py -d ./email-archives -m email
```

### Code Helper

**Purpose**: Handles source code files with language-specific optimizations.

**Key Features**:
- Detects programming language automatically
- Preserves code structure and important comments
- Handles import statements and boilerplate
- Language-specific optimizations for Python, JavaScript, etc.

**Usage**:
```bash
python optimize.py -d ./source-code -m code
```

### Documentation Helper

**Purpose**: Processes documentation content with focus on readability.

**Key Features**:
- Handles markdown headings, code blocks, and tables properly
- Cleans navigation elements while preserving structure
- Handles tables of contents and breadcrumbs
- Preserves important version information

**Usage**:
```bash
python optimize.py -d ./documentation -m docs
```

### Markdown Helper

**Purpose**: Optimizes Markdown and HTML content with focus on content.

**Key Features**:
- Handles mixed Markdown and HTML content
- Cleans unnecessary HTML while preserving structure
- Processes images, links, and formatting
- Handles YAML frontmatter

**Usage**:
```bash
python optimize.py -d ./markdown-content -m markdown
```

## Helper Configuration Options

Each specialized helper accepts configuration options that can be set programmatically. Below are the available options for each helper:

### Notion Helper Options

| Option | Default | Description |
|--------|---------|-------------|
| `preserve_callouts` | `True` | Keep Notion callout blocks (e.g., 📝, 💡) |
| `preserve_toggles` | `True` | Keep Notion toggle/expandable blocks |
| `include_id_comments` | `True` | Add HTML comments with Notion IDs for reference |
| `convert_properties` | `True` | Convert Notion Properties to YAML frontmatter |

### Email Helper Options

| Option | Default | Description |
|--------|---------|-------------|
| `preserve_headers` | `False` | Keep email headers (From, To, Subject, etc.) |
| `preserve_quotes` | `False` | Keep quoted text from earlier messages |
| `preserve_signatures` | `False` | Keep email signatures |
| `max_quote_depth` | `1` | Maximum levels of quoted text to retain |

### Code Helper Options

| Option | Default | Description |
|--------|---------|-------------|
| `remove_boilerplate` | `True` | Remove license/copyright headers |
| `remove_logs` | `False` | Remove log/print statements |
| `preserve_todos` | `True` | Keep TODO/FIXME comments |
| `preserve_imports` | `True` | Keep import statements unmodified |

### Documentation Helper Options

| Option | Default | Description |
|--------|---------|-------------|
| `preserve_toc` | `True` | Keep table of contents |
| `preserve_breadcrumbs` | `False` | Keep navigation breadcrumbs |
| `preserve_edit_info` | `False` | Keep "last updated" information |
| `preserve_version_info` | `True` | Keep version numbers |

### Markdown Helper Options

| Option | Default | Description |
|--------|---------|-------------|
| `preserve_html` | `True` | Keep HTML tags |
| `preserve_comments` | `False` | Keep HTML comments |
| `preserve_images` | `True` | Keep image links |
| `preserve_badges` | `False` | Keep badges/shields |
| `preserve_frontmatter` | `True` | Keep YAML frontmatter |
| `fix_redundant_links` | `True` | Simplify redundant links |
| `fix_relative_links` | `False` | Convert relative links to text |

## Interpreting Reports

The generated report provides valuable insights into the optimization process:

### Key Report Sections

1. **Configuration Summary**: Shows input source, mode, and scan configuration
2. **Content Type Detection**: (Auto mode only) Breakdown of detected content types
3. **Optimization Statistics**: Character and token counts before and after optimization
4. **Optimizations Applied**: Details the specific optimizations that were performed
5. **Warnings and Issues**: Lists any problems encountered during processing

### Analyzing Effectiveness

- **Character/Token Reduction**: Higher percentages indicate more noise was removed
- **Content Type Distribution**: Shows the mix of content in your repository (in auto mode)
- **Processing Speed**: Can help identify if there were performance issues

### Understanding Statistics Table

```
| Metric | Original | Optimized | Reduction |
|--------|----------|-----------|-----------|
| Character Count | 1,234,567 | 987,654 | 20.00% |
| Token Count | 246,913 | 197,530 | 20.00% |
| Files Processed | 123 | | |
| Files Skipped | 45 | | |
| Processing Time | 12.34 seconds | | |
```

This table shows:
- Original and optimized content size in characters and tokens
- The percentage reduction achieved through optimization
- How many files were processed or skipped
- How long the process took

## Troubleshooting

### Common Issues and Solutions

#### Issue: Missing Optional Dependencies

**Symptoms**: Warnings about tiktoken, gitignore-parser, or other libraries being unavailable.

**Solution**: Install the missing packages:
```bash
pip install tiktoken gitignore-parser pygments beautifulsoup4 mail-parser
```

#### Issue: No Files Found During Directory Scan

**Symptoms**: Report indicates no files were processed.

**Solutions**:
- Check if your `--extensions` parameter matches the files in your directory
- Verify your `--ignore` patterns aren't excluding everything
- Check file permissions
- Try running with more verbose output: `python -v optimize.py ...`

#### Issue: Unexpected Removal of Content

**Symptoms**: Important content is missing from the optimized output.

**Solutions**:
- Try using `code` mode instead of `docs` mode for less aggressive optimization
- Check if auto-detection incorrectly classified your content
- Check the report to see which optimizations were applied
- Configure helpers to preserve specific content types

#### Issue: Content Detection Not Working as Expected

**Symptoms**: Files are being optimized with the wrong content helper.

**Solution**:
- Specify the mode explicitly instead of using auto-detection
- Check file extensions to ensure they match the content type
- Review the detection confidence scores in the report

#### Issue: Error Reading Files

**Symptoms**: Errors about file encoding or permissions.

**Solutions**:
- Check file permissions
- Ensure files are readable text files, not binary
- Specify an explicit encoding if needed
- Use `--ignore` to skip problematic files

#### Issue: Memory Usage Too High

**Symptoms**: Out of memory errors when processing large repositories.

**Solutions**:
- Process directories in smaller chunks
- Use more targeted file extensions to limit processing
- Process one file at a time for very large files

## Use Cases and Examples

### Use Case 1: Preparing Documentation for Fine-Tuning an LLM

```bash
python optimize.py -d ./product-docs -m docs --extensions .md,.txt,.html \
    --ignore "drafts/,archive/,images/" --use-gitignore
```

This setup:
- Processes product documentation files with extensions .md, .txt, and .html
- Ignores drafts, archive materials, and images directories
- Respects any .gitignore rules in the repository

### Use Case 2: Preparing Mixed Repository Content

```bash
python optimize.py -a ./mixed-repository \
    -o ./optimized/cleaned-content.md \
    --report_file ./optimized/report.md
```

This workflow:
- Automatically detects and applies the best optimization for each file type
- Handles code, documentation, markup, and other content types appropriately
- Generates a detailed report showing content type distribution
- Outputs all optimized content to a single file for easy reference

### Use Case 3: Optimizing a Large Documentation Site Scrape

```bash
python optimize.py -d ./scraped-docs -m docs \
    --extensions .html,.htm,.txt,.md \
    --ignore "*.css,*.js,*.svg,*.png,*.jpg,assets/,images/" \
    --policy-filter -o ./clean-docs.md
```

This setup:
- Processes HTML and text files from a scraped documentation site
- Ignores assets and image files
- Filters out policy pages
- Outputs to a single markdown file

### Use Case 4: Processing Email Threads for Context Retrieval

```bash
python optimize.py -d ./email-export -m email \
    --extensions .eml,.txt --ignore "spam/,drafts/" \
    -o ./processed/emails-cleaned.md
```

This setup:
- Processes .eml and .txt files containing email content
- Ignores spam and drafts folders
- Removes email signatures, disclaimers, and repeated headers
- Limits quote depth to enhance readability
- Outputs to a single markdown file for easy reference

### Use Case 5: Processing a Notion Export for Documentation

```bash
python optimize.py -n ./notion-export \
    -o ./cleaned/notion-content.md \
    --report_file ./cleaned/notion-report.md
```

This setup:
- Processes Notion export content with specialized handling
- Cleans up Notion IDs from filenames while preserving the references
- Converts Notion properties blocks to YAML frontmatter
- Optimizes Notion-specific artifacts and formatting

### Use Case 6: Preparing Source Code for Model Training

```bash
python optimize.py -d ./code-repository -m code \
    --extensions .py,.js,.ts,.java,.cpp \
    --ignore "tests/,*.test.*,vendor/,node_modules/" \
    -o ./training-data/code-sample.md
```

This setup:
- Processes code files with extensions matching common programming languages
- Ignores test code, vendor code, and node modules
- Preserves code structure and important comments
- Removes boilerplate headers while keeping functional code

## Command Line Reference

```
usage: optimize.py [-h] (-d INPUT_DIR | -i INPUT_FILE | -q DIR | -n DIR | -a DIR)
                   [-o OUTPUT_FILE] [-m {code,docs,notion,email,markdown,auto}]
                   [--report_file REPORT_FILE] [--extensions EXTENSIONS]
                   [--ignore IGNORE] [--use-gitignore]
                   [--policy-filter | --no-policy-filter]

options:
  -h, --help            show this help message and exit
  -d INPUT_DIR, --input_dir INPUT_DIR
                        Path to the root directory of the content to scan.
  -i INPUT_FILE, --input_file INPUT_FILE
                        Path to the input file (e.g., a Repomix file).
  -q DIR, --quick DIR   Quick optimization with sensible defaults (docs mode)
  -n DIR, --notion DIR  Process a Notion.so export directory
  -a DIR, --auto DIR    Auto-detect content types
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path for the optimized output file. If omitted, generated
                        automatically based on input name and timestamp.
  -m {code,docs,notion,email,markdown,auto}, --mode {code,docs,notion,email,markdown,auto}
                        Optimization mode. Use 'auto' for content type detection.
  --report_file REPORT_FILE
                        Path for the optimization report file.
  --extensions EXTENSIONS
                        Comma-separated list of file extensions to include.
  --ignore IGNORE       Comma-separated list of glob patterns to ignore.
  --use-gitignore       Respect .gitignore rules during scanning.
  --policy-filter       Enable filtering of potential policy pages (default).
  --no-policy-filter    Disable filtering of policy pages (process all files).
```

## Conclusion

Content Optimizer offers a powerful way to prepare text content for LLM consumption. By removing unnecessary boilerplate and noise, you can:

- Reduce token usage (and therefore costs)
- Improve the signal-to-noise ratio of your content
- Focus the LLM on the most important information

With specialized content helpers, you can now achieve even better results across different content types. Experiment with different configurations to find the optimal balance between noise removal and content preservation for your specific use case.
