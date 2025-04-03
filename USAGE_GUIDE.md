# Content Optimizer: Comprehensive Usage Guide

This guide provides detailed instructions and best practices for using the Content Optimizer tool to prepare content for Large Language Model (LLM) consumption.

## Table of Contents

- [Understanding How Content Optimizer Works](#understanding-how-content-optimizer-works)
- [Installation and Setup](#installation-and-setup)
- [Basic Usage Workflows](#basic-usage-workflows)
- [Advanced Configuration](#advanced-configuration)
- [Understanding Optimization Rules](#understanding-optimization-rules)
- [Interpreting Reports](#interpreting-reports)
- [Troubleshooting](#troubleshooting)
- [Use Cases and Examples](#use-cases-and-examples)

## Understanding How Content Optimizer Works

Content Optimizer uses regular expression patterns defined in `optimization_rules.py` to identify and remove common "noise" elements from text content. These elements typically include:

- Website navigation menus, headers, and footers
- Contact forms and subscription boxes
- Tracking pixels and metadata
- Redundant information and formatting
- Policy content (optional)

The tool works in two primary modes:

- **docs mode**: More aggressive optimization suitable for web content and documentation
- **code mode**: More conservative optimization suitable for source code repositories

The optimization process follows these steps:

1. **Input Processing**: Read content from a directory or a Repomix file
2. **Optimization**: Apply regex patterns to remove noise elements
3. **Output Generation**: Produce a cleaned file and a detailed report

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

# Install optional dependencies
pip install tiktoken gitignore-parser
```

### Verifying Your Installation

Run a simple test to verify everything is working:

```bash
python optimize.py -h
```

This should display the help message with all available options.

## Basic Usage Workflows

### Workflow 1: Optimizing Documentation for an LLM

```bash
# Basic documentation optimization
python optimize.py -d ./my-docs -m docs

# Specifying custom output location
python optimize.py -d ./my-docs -o ./optimized/clean-docs.md -m docs --report_file ./optimized/report.md
```

### Workflow 2: Processing a Source Code Repository

```bash
# Process source code with less aggressive optimization
python optimize.py -d ./my-code-repo -m code

# Focus only on specific file types
python optimize.py -d ./my-code-repo -m code --extensions .py,.js,.md
```

### Workflow 3: Processing a Repomix File

```bash
# Process a standard Repomix file
python optimize.py -i ./repomix-output.txt -m docs

# Process a Repomix file but keep policy pages
python optimize.py -i ./repomix-output.txt -m docs --no-policy-filter
```

## Advanced Configuration

### Custom File Selection

Fine-tune which files are processed when scanning directories:

```bash
# Include only specific file types
python optimize.py -d ./content --extensions .md,.txt,.html,.rst

# Ignore specific patterns
python optimize.py -d ./content --ignore "draft/,*-old.md,_archive/,temp/"

# Respect .gitignore rules (requires gitignore-parser package)
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

## Understanding Optimization Rules

The optimization rules are defined in `optimization_rules.py` as regular expressions. They're ordered from most specific to most general to avoid over-removing content:

1. **Metadata/Artifacts**: Specific publisher metadata, tracking elements
2. **Website Chrome**: Navigation, headers, footers, sidebars
3. **Prompts/Forms**: Comment prompts, contact forms, subscription boxes
4. **Links/Tracking**: Redundant links, tracking pixels
5. **Formatting/Structure**: Excessive spacing, redundant headers

You can examine the report after optimization to see which rules were triggered and how frequently.

## Interpreting Reports

The generated report provides valuable insights into the optimization process:

### Key Report Sections

1. **Configuration Summary**: Shows input source, mode, and scan configuration
2. **Optimization Statistics**: Character and token counts before and after optimization
3. **Optimizations Applied**: Summarizes which categories of optimizations were most common
4. **Rule Trigger Statistics**: Detailed breakdown of how many times each rule was triggered
5. **Policy Pages Handling**: Lists which files were identified as policy pages (if any)
6. **Warnings**: Any issues encountered during processing

### Analyzing Effectiveness

- **Character/Token Reduction**: Higher percentages indicate more noise was removed
- **Most Frequent Optimizations**: Shows what types of noise dominated your content
- **Processing Speed**: Can help identify if there were performance issues

## Troubleshooting

### Common Issues and Solutions

#### Issue: Missing Optional Dependencies

**Symptoms**: Warnings about tiktoken or gitignore-parser being unavailable.

**Solution**: Install the missing packages:
```bash
pip install tiktoken gitignore-parser
```

#### Issue: No Files Found During Directory Scan

**Symptoms**: Report indicates no files were processed.

**Solutions**:
- Check if your `--extensions` parameter matches the files in your directory
- Verify your `--ignore` patterns aren't excluding everything
- Check file permissions

#### Issue: Unexpected Removal of Content

**Symptoms**: Important content is missing from the optimized output.

**Solutions**:
- Try using `code` mode instead of `docs` mode for less aggressive optimization
- Check the report to see which rules were triggered most frequently
- Consider modifying the patterns in `optimization_rules.py` if needed

#### Issue: Policy Filter Removing Needed Content

**Symptoms**: Important files are being identified as policy pages and excluded.

**Solution**: Use the `--no-policy-filter` option to include all content.

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

### Use Case 2: Preparing Multiple Github Repositories

Create a shell script (`batch-optimize.sh`):

```bash
#!/bin/bash
REPOS_DIR="./repositories"
OUTPUT_DIR="./optimized-repos"

mkdir -p $OUTPUT_DIR

for repo in $(ls $REPOS_DIR); do
  echo "Processing repository: $repo"
  python optimize.py -d "$REPOS_DIR/$repo" -m code \
    -o "$OUTPUT_DIR/$repo-optimized.md" \
    --report_file "$OUTPUT_DIR/$repo-report.md" \
    --use-gitignore
done
```

Make it executable and run:
```bash
chmod +x batch-optimize.sh
./batch-optimize.sh
```

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

### Use Case 4: Preparing Context for a RAG System

```bash
# First optimize the content
python optimize.py -d ./knowledge-base -m docs -o ./processed/cleaned-kb.md

# Then you can use the optimized content in your RAG system
# (Example command for a hypothetical embedding tool)
embed-tool process --input ./processed/cleaned-kb.md --output ./embeddings/kb-embeddings
```

This workflow:
1. Optimizes a knowledge base to remove noise and reduce token usage
2. Uses the cleaned content for embedding generation in a RAG system

## Conclusion

Content Optimizer offers a powerful way to prepare text content for LLM consumption. By removing unnecessary boilerplate and noise, you can:

- Reduce token usage (and therefore costs)
- Improve the signal-to-noise ratio of your content
- Focus the LLM on the most important information

Experiment with different configurations to find the optimal balance between noise removal and content preservation for your specific use case.
