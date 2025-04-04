# Content Optimizer Helper Configuration

This document provides detailed information about the configuration options available for each specialized content helper. While the default settings work well for most cases, you may want to customize the behavior for specific use cases.

## Configuration Overview

Each content helper can be configured with specific options that control how it processes content. These settings determine what elements are preserved or removed during optimization.

## LLM Training Data Generator

The LLM Training Data Generator converts optimized content into training data formats suitable for fine-tuning Large Language Models.

### Basic Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `data_format` | `instruction` | The format of the training data to generate: instruction, conversation, completion, question-answer, or general |
| `output_format` | `jsonl` | The output file format: jsonl, csv, parquet (if pandas available), or hf_dataset (if datasets available) |
| `max_examples` | `10000` | Maximum number of examples to generate per file |
| `min_token_count` | `50` | Minimum token count for examples to include |
| `max_token_count` | `1024` | Maximum token count for examples to include |
| `include_metadata` | `True` | Whether to include metadata in generated examples |
| `split_sections` | `True` | Whether to split content into sections for processing |
| `verbose` | `True` | Whether to enable verbose output |

### Usage Example

```bash
# Generate instruction-tuning data in JSONL format
python generate_training_data.py -i ./optimized-content.md -f instruction

# Generate conversation data with customized token limits
python generate_training_data.py -i ./optimized-content.md -f conversation --min_tokens 100 --max_tokens 2048

# Generate a comprehensive dataset with multiple formats
python generate_training_data.py -i "./optimized-*.md" -f general --output_format csv
```

### Data Format Details

#### Instruction Format

```json
{
  "instruction": "Summarize the key points in this file",
  "input": "Content to process...",
  "output": "Summary of the content..."
}
```

#### Conversation Format

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What does this code do?"},
    {"role": "assistant", "content": "This code implements a function to..."}
  ]
}
```

#### Completion Format

```json
{
  "prompt": "def calculate_factorial(n):",
  "completion": "    if n == 0 or n == 1:\n        return 1\n    else:\n        return n * calculate_factorial(n-1)"
}
```

#### Question-Answer Format

```json
{
  "question": "What is the purpose of this function?",
  "answer": "This function calculates the factorial of a number using recursion."
}
```

### Amazon Q Completion Format

To generate training data compatible with Amazon Q, you can use a custom configuration file:

```json
{
  "schema_version": "1.0",
  "completion_type": "code",
  "specifications": {
    "tool_name": "AmazonQCompletions",
    "model_id": "amazon.titan-code-generator-v1",
    "training_data_format": {
      "format_type": "completion",
      "input_field": "prefix",
      "output_field": "completion",
      "metadata_fields": [
        "language",
        "source_file",
        "file_context"
      ]
    }
  },
  "conversion_settings": {
    "output_format": "jsonl",
    "token_limit": {
      "min_input_tokens": 30,
      "max_input_tokens": 512,
      "max_output_tokens": 1024
    }
  }
}
```

You can then generate Amazon Q compatible data with:

```bash
python generate_training_data.py -i ./optimized-code.md -f completion \
  -c ./amazonq-completion-specs.json -o ./amazonq-data
```

The output will be in JSONL format with each example having:
- `prefix`: The code context/prompt
- `completion`: The generated code completion
- Metadata: language, source_file, file_context

### Advanced Configuration

You can create a JSON configuration file with custom settings:

```json
{
  "data_format": "instruction",
  "output_format": "jsonl",
  "max_examples": 5000,
  "min_token_count": 100,
  "max_token_count": 2048,
  "include_metadata": true,
  "split_sections": true,
  "separator": "================================================================"
}
```

And use it with the `-c` flag:

```bash
python generate_training_data.py -i ./optimized-content.md -c ./config.json
```

## Universal Configuration Options

These options apply to all helpers:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | Varies | Display name of the helper (for reporting) |

## Notion Helper Configuration

The Notion helper (`NotionHelper`) optimizes Notion.so exports by handling Notion-specific artifacts.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preserve_callouts` | bool | `True` | Keep Notion callout blocks (e.g., 📝, 💡) |
| `preserve_toggles` | bool | `True` | Keep Notion toggle/expandable blocks |
| `include_id_comments` | bool | `True` | Add HTML comments with Notion IDs for reference |
| `convert_properties` | bool | `True` | Convert Notion Properties to YAML frontmatter |

### Example Usage

```python
from content_helpers import get_content_helper

# Get Notion helper with custom configuration
helper = get_content_helper('notion', preserve_toggles=False, include_id_comments=False)

# Process a file
optimized_content, stats = helper.process_file('path/to/file.md')
```

## Email Helper Configuration

The Email helper (`EmailHelper`) optimizes email content by cleaning signatures, headers, and quoted text.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preserve_headers` | bool | `False` | Keep email headers (From, To, Subject, etc.) |
| `preserve_quotes` | bool | `False` | Keep quoted text from earlier messages |
| `preserve_signatures` | bool | `False` | Keep email signatures |
| `max_quote_depth` | int | `1` | Maximum levels of quoted text to retain |

### Example Usage

```python
from content_helpers import get_content_helper

# Get Email helper with custom configuration
helper = get_content_helper('email', preserve_headers=True, max_quote_depth=2)

# Process a file
optimized_content, stats = helper.process_file('path/to/email.eml')
```

## Code Helper Configuration

The Code helper (`CodeHelper`) optimizes source code files by handling boilerplate while preserving important code structure.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `remove_boilerplate` | bool | `True` | Remove license/copyright headers |
| `remove_logs` | bool | `False` | Remove log/print statements |
| `preserve_todos` | bool | `True` | Keep TODO/FIXME comments |
| `preserve_imports` | bool | `True` | Keep import statements unmodified |

### Example Usage

```python
from content_helpers import get_content_helper

# Get Code helper with custom configuration
helper = get_content_helper('code', remove_logs=True, preserve_todos=False)

# Process a file
optimized_content, stats = helper.process_file('path/to/source.py')
```

## Documentation Helper Configuration

The Documentation helper (`DocsHelper`) optimizes documentation content by handling typical document structure.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preserve_toc` | bool | `True` | Keep table of contents |
| `preserve_breadcrumbs` | bool | `False` | Keep navigation breadcrumbs |
| `preserve_edit_info` | bool | `False` | Keep "last updated" information |
| `preserve_version_info` | bool | `True` | Keep version numbers |

### Example Usage

```python
from content_helpers import get_content_helper

# Get Documentation helper with custom configuration
helper = get_content_helper('docs', preserve_toc=False, preserve_version_info=False)

# Process a file
optimized_content, stats = helper.process_file('path/to/readme.md')
```

## Markdown Helper Configuration

The Markdown helper (`MarkdownHelper`) optimizes Markdown and HTML content by handling typical web content elements.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preserve_html` | bool | `True` | Keep HTML tags |
| `preserve_comments` | bool | `False` | Keep HTML comments |
| `preserve_images` | bool | `True` | Keep image links |
| `preserve_badges` | bool | `False` | Keep badges/shields |
| `preserve_frontmatter` | bool | `True` | Keep YAML frontmatter |
| `fix_redundant_links` | bool | `True` | Simplify redundant links |
| `fix_relative_links` | bool | `False` | Convert relative links to text |

### Example Usage

```python
from content_helpers import get_content_helper

# Get Markdown helper with custom configuration
helper = get_content_helper('markdown', preserve_html=False, preserve_images=False)

# Process a file
optimized_content, stats = helper.process_file('path/to/document.md')
```

## Unified Optimizer Configuration

The Unified Optimizer (`UnifiedOptimizer`) provides auto-detection and routing to appropriate helpers.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_mode` | string | `"docs"` | Fallback mode if auto-detection fails |

You can also pass configuration options for specific helpers, which will be forwarded to those helpers when they're used.

### Example Usage

```python
from content_helpers import get_unified_optimizer

# Get a Unified Optimizer with custom configurations for specific helpers
optimizer = get_unified_optimizer(
    default_mode="markdown",
    # Email helper options
    preserve_headers=True,
    max_quote_depth=2,
    # Code helper options  
    remove_logs=True
)

# Process a file with auto-detection
optimized_content, stats = optimizer.optimize_file('path/to/file')
```

## Advanced: Creating Custom Optimization Profiles

You can create custom optimization profiles by defining configuration presets for different scenarios:

```python
# Define optimization profiles as dictionaries
PROFILES = {
    "minimal": {
        # Keep only essential content
        "preserve_images": False,
        "preserve_html": False,
        "preserve_toc": False,
        "preserve_breadcrumbs": False,
        "preserve_edit_info": False,
        "preserve_version_info": False,
        "remove_boilerplate": True,
        "remove_logs": True
    },
    "complete": {
        # Keep most content intact
        "preserve_images": True,
        "preserve_html": True,
        "preserve_toc": True,
        "preserve_comments": True,
        "preserve_breadcrumbs": True,
        "preserve_edit_info": True,
        "preserve_version_info": True
    }
}

# Use a profile with a helper
from content_helpers import get_content_helper

helper = get_content_helper('markdown', **PROFILES["minimal"])
```

## Extending Helper Configuration

To add new configuration options to an existing helper:

1. Add the new option to the helper's `__init__` method with a default value
2. Update the helper's processing logic to use the new option
3. Document the new option in this file

Example:

```python
def __init__(self, **kwargs):
    super().__init__(name="MyHelper", **kwargs)
    # Add new configuration option with default
    self.new_option = kwargs.get('new_option', default_value)
```
