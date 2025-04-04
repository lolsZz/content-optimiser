#!/usr/bin/env python3
"""
Content Optimization Tool for LLM Processing

This script takes raw text content, either from a single structured file (like one
produced by Repomix) or by scanning a directory of files, and applies intelligent
optimization to remove noise, boilerplate, and unnecessary content.

The tool now features specialized helpers for different content types:
- 'docs': Optimized for documentation or web-scraped content
- 'code': Optimized for source code repositories
- 'notion': Specialized handling for Notion.so exports
- 'email': Optimized for email content and threads
- 'markdown': Enhanced for Markdown and HTML content
- 'auto': Automatically detect and apply the best optimizations for each file

The script generates:
1. An optimized output file containing the cleaned content.
2. A detailed markdown report summarizing the optimization process and results.

Optional Dependencies:
- tiktoken: For accurate LLM token counting (used for stats).
- gitignore-parser: To respect `.gitignore` rules when scanning directories.
- pygments: For better code detection and language identification.
- beautifulsoup4: For better HTML parsing in markdown content.
- mail-parser: For structured parsing of email content.
"""

import re
import os
import argparse
import sys
from datetime import datetime
import time
import fnmatch
from pathlib import Path
import traceback
import shutil
from collections import defaultdict

# Check for tqdm (progress bar)
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm = lambda x, **kwargs: x  # Simple passthrough

# Check for tiktoken availability
try:
    import tiktoken
    TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    TOKEN_ENCODING = None
except Exception as e:
    TIKTOKEN_AVAILABLE = False
    TOKEN_ENCODING = None

# Check for gitignore-parser availability
try:
    import gitignore_parser
    GITIGNORE_AVAILABLE = True
except ImportError:
    GITIGNORE_AVAILABLE = False
    gitignore_parser = None

# Update import statements to use the restructured directories
try:
    import optimization_rules as rules
    # Import specialized content helpers
    from content_helpers import get_content_helper, get_unified_optimizer
    CONTENT_HELPERS_AVAILABLE = True
except ImportError as e:
    print(f"Error: Required module not found. {e}", file=sys.stderr)
    CONTENT_HELPERS_AVAILABLE = False

# --- Configuration Constants ---
VERSION = "2.0.0"
DEFAULT_MODE = "docs"
SUPPORTED_MODES = ["code", "docs", "notion", "email", "markdown", "auto"]
DEFAULT_SCAN_EXTENSIONS = ".py,.md,.ipynb,.sh,.yaml,.yml,.toml,.json,.css,.js,.ts,.html,.txt,.rst"
DEFAULT_IGNORE_PATTERNS = ".git,.hg,.svn,build,dist,node_modules,__pycache__,*.pyc,*.log,.DS_Store,.env*,.vscode,.idea,.venv,venv,*.bin,*.img,*.jpg,*.jpeg,*.png,*.gif,*.zip,*.tar.gz,*.pdf,*.doc*,*.xls*,*.ppt*,*.o,*.so,*.a,*.dll,*.lib,*.class,*.jar,*.war,*.onnx,*.pb,*.pt,*.pth,*.h5,*.keras,*.sqlite,*.db"
OPTIMIZED_SECTION_SEPARATOR = "================================================================"
OPTIMIZED_FILE_SEPARATOR_FORMAT = "--- FILE: {file_path} ---"
OPTIMIZED_HEADER_FORMAT = "Repository Snapshot (Optimized for: {mode}, Source: {source_type})"
DEFAULT_POLICY_FILTER = True

# --- Color and styling definitions ---
try:
    COLORIZE = sys.stdout.isatty() and os.name != 'nt'
except:
    COLORIZE = False

# ANSI color/style codes
if COLORIZE:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"
else:
    GREEN = YELLOW = RED = BLUE = MAGENTA = CYAN = BOLD = UNDERLINE = RESET = ""

# --- Helper Functions ---

def print_header(text):
    """Prints a styled header to the console"""
    term_width = shutil.get_terminal_size().columns
    separator = "=" * (min(term_width, 80))
    print(f"\n{BOLD}{BLUE}{separator}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{separator}{RESET}\n")

def print_success(text):
    """Prints a success message with green color"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Prints a warning message with yellow color"""
    print(f"{YELLOW}⚠ Warning: {text}{RESET}", file=sys.stderr)

def print_error(text):
    """Prints an error message with red color"""
    print(f"{RED}✗ Error: {text}{RESET}", file=sys.stderr)

def print_info(text):
    """Prints an info message with cyan color"""
    print(f"{CYAN}ℹ {text}{RESET}")

def count_tokens(text: str) -> int:
    """
    Counts tokens using the tiktoken library (cl100k_base encoding).
    Returns -1 if tiktoken is unavailable or fails.
    """
    if not TIKTOKEN_AVAILABLE or TOKEN_ENCODING is None:
        return -1
    try:
        return len(TOKEN_ENCODING.encode(text))
    except Exception as e:
        # Add a flag to warn only once per run to avoid flooding stderr
        if not hasattr(count_tokens, "warned"):
            print_warning(f"Tiktoken counting failed. Error: {e}. Subsequent errors will be suppressed.")
            count_tokens.warned = True
        return -1

def format_stat(value) -> str:
    """Formats statistics (numbers, percentages, N/A) for display in the report."""
    if value == -1:
        return "N/A (tiktoken unavailable)"
    elif isinstance(value, float):
        return f"{value:.2f}%"
    else:
        try:
            return f"{value:,}"
        except (ValueError, TypeError):
            return str(value)

# --- Directory Scanning Logic ---

def read_gitignore(directory: str) -> callable:
    """
    Parses a .gitignore file in the specified directory if gitignore-parser is available.
    Returns a callable function that returns True if a path matches the rules.
    """
    gitignore_path = Path(directory) / ".gitignore"
    if GITIGNORE_AVAILABLE and gitignore_path.is_file():
        try:
            if not gitignore_parser: raise ImportError("gitignore_parser failed to load.")
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                matches = gitignore_parser.parse(f)
                print_info(f"Successfully parsed .gitignore at {gitignore_path}")
                return matches
        except Exception as e:
            print_warning(f"Could not parse .gitignore file at {gitignore_path}: {e}. Proceeding without gitignore rules.")
    elif not GITIGNORE_AVAILABLE and gitignore_path.is_file():
        print_warning(f".gitignore file found at {gitignore_path} but 'gitignore-parser' library not installed.")
    
    # Return a dummy function that never matches
    return lambda x: False

def is_ignored(path_to_check: Path, root_dir: Path, ignore_patterns: list[str], gitignore_matcher: callable) -> bool:
    """
    Checks if a given path should be ignored based on glob patterns or .gitignore rules.
    """
    try:
        abs_path_to_check = path_to_check.resolve()
        abs_root_dir = root_dir.resolve()

        if abs_path_to_check == abs_root_dir:
            relative_path = Path('.')
        else:
            try:
                relative_path = abs_path_to_check.relative_to(abs_root_dir)
            except ValueError:
                return False

        relative_path_posix = relative_path.as_posix()
        base_name = relative_path.name

    except OSError as e:
        print_warning(f"Could not resolve path {path_to_check} relative to {root_dir}. Error: {e}")
        return True

    # Check against user-provided glob patterns
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(relative_path_posix, pattern) or fnmatch.fnmatchcase(base_name, pattern):
            return True
        
        # Check directory pattern
        if pattern.endswith('/'):
            pattern_dir = pattern.rstrip('/')
            for part in relative_path.parts:
                if fnmatch.fnmatchcase(part, pattern_dir):
                    potential_dir_path = abs_root_dir / Path(*relative_path.parts[:relative_path.parts.index(part)+1])
                    if potential_dir_path.is_dir():
                        return True

    # Check against .gitignore rules
    if gitignore_matcher and callable(gitignore_matcher):
        try:
            if gitignore_matcher(str(abs_path_to_check)):
                return True
        except Exception as e:
            print_warning(f"gitignore_parser failed for path {abs_path_to_check}: {e}")

    return False

def is_likely_text_file(filepath: str, block_size=1024) -> bool:
    """
    Check if a file is likely text-based by looking for null bytes in the first block.
    """
    try:
        with open(filepath, 'rb') as f:
            block = f.read(block_size)
        
        # Check for UTF-8 BOM
        if block.startswith(b'\xef\xbb\xbf'):
            return b'\0' not in block[3:]
        else:
            return b'\0' not in block
    except OSError as e:
        print_warning(f"Could not read file {filepath} to check type: {e}")
        return False
    except Exception as e:
        print_warning(f"Unexpected error checking file type for {filepath}: {e}")
        return False

def scan_directory(root_dir: str, extensions: set[str], ignore_patterns: list[str], use_gitignore: bool, warnings_list: list[str]) -> tuple[list[str], int]:
    """
    Scans a directory recursively for files with specified extensions, respecting
    ignore patterns and optionally .gitignore. Skips binary files.
    """
    included_files = []
    skipped_count = 0
    root_path = Path(root_dir).resolve()

    # Initialize gitignore matcher
    gitignore_matcher = None
    if use_gitignore:
        try:
            gitignore_matcher = read_gitignore(str(root_path))
        except Exception as e:
            warnings_list.append(f"Failed to initialize gitignore processing: {e}")
            print_warning(f"Failed to initialize gitignore processing: {e}")

    print_header("Directory Scan")
    print_info(f"Scanning directory: {root_path}")
    print_info(f"Including extensions: {', '.join(sorted(list(extensions))) or 'All text files'}")
    ignore_pats_str = ', '.join(f"`{p}`" for p in ignore_patterns) if ignore_patterns else 'None'
    print_info(f"Ignoring patterns: {ignore_pats_str}")
    gitignore_status = 'Yes' if use_gitignore else 'No'
    if use_gitignore and not GITIGNORE_AVAILABLE: gitignore_status += ' (parser unavailable)'
    print_info(f"Using .gitignore: {gitignore_status}")

    # Calculate total files for progress bar
    total_files_estimate = 0
    for _, _, files in os.walk(str(root_path)):
        total_files_estimate += len(files)
    
    progress_bar = tqdm(total=total_files_estimate, desc="Scanning files", unit="file") if TQDM_AVAILABLE else None
    
    for dirpath_str, dirnames, filenames in os.walk(str(root_path), topdown=True, onerror=lambda e: warnings_list.append(f"Scan error: {e}")):
        dirpath = Path(dirpath_str)

        # Filter out ignored directories
        dirs_to_process = []
        original_dir_count = len(dirnames)
        for d in dirnames:
            full_dir_path = dirpath / d
            if not is_ignored(full_dir_path, root_path, ignore_patterns, gitignore_matcher):
                dirs_to_process.append(d)

        skipped_dir_count = (original_dir_count - len(dirs_to_process))
        if skipped_dir_count > 0:
            skipped_count += skipped_dir_count
        dirnames[:] = dirs_to_process

        # Process files in the current directory
        for filename in filenames:
            if progress_bar:
                progress_bar.update(1)
            full_file_path = dirpath / filename

            # Check if the file is ignored
            if is_ignored(full_file_path, root_path, ignore_patterns, gitignore_matcher):
                skipped_count += 1
                continue

            # Check file extension
            file_ext_lower = full_file_path.suffix.lower()
            if extensions and file_ext_lower not in extensions:
                skipped_count += 1
                continue

            # Check if the file is text-based
            try:
                if is_likely_text_file(str(full_file_path)):
                    relative_path = full_file_path.relative_to(root_path).as_posix()
                    included_files.append(relative_path)
                else:
                    relative_path = full_file_path.relative_to(root_path).as_posix()
                    warnings_list.append(f"Skipped likely binary file: {relative_path}")
                    skipped_count += 1
            except Exception as e:
                try:
                    relative_path_str = str(full_file_path.relative_to(root_path))
                except Exception:
                    relative_path_str = "Unknown Path"
                error_msg = f"Error processing file {relative_path_str}, skipping. Error: {e}"
                print_warning(error_msg)
                warnings_list.append(error_msg)
                skipped_count += 1
    
    if progress_bar:
        progress_bar.close()

    print_success(f"Scan found {len(included_files)} files to include")
    if skipped_count > 0:
        print_info(f"Skipped {skipped_count} files/directories based on ignores, extension mismatch, binary type, or errors")

    # Sort files for consistent output
    included_files.sort()
    return included_files, skipped_count

def generate_directory_tree(file_paths: list[str], clean_notion_ids: bool = False) -> str:
    """
    Generates a Markdown code block containing a textual representation
    of the directory structure based on the provided list of relative file paths.
    """
    # Check if any file paths are provided
    if not file_paths:
        return "```\nNo files found\n```"
    
    # Create a tree structure from the file paths
    tree = {}
    for path in file_paths:
        # Handle potential None values in file paths
        if path is None:
            continue
            
        # Use cleaned path if processing Notion content
        if clean_notion_ids:
            try:
                from content_helpers.notion_helper import extract_notion_id
                parts = []
                for part in path.split('/'):
                    clean_name, _ = extract_notion_id(part)
                    parts.append(clean_name if clean_name is not None else part)
                path = '/'.join(parts)
            except (ImportError, AttributeError):
                # Fall back to original path if Notion helper not available
                pass
                
        # Split path into components
        parts = path.split('/')
        current = tree
        for part in parts[:-1]:  # Process directories
            if part not in current:
                current[part] = {}
            current = current[part]
        # Add the file (leaf node)
        if parts[-1]:
            current[parts[-1]] = None

    # Generate the tree representation
    lines = ["```"]
    
    # Handle empty tree edge case
    if not tree:
        lines.append("No valid directory structure found")
        lines.append("```")
        return "\n".join(lines)
    
    def print_tree(node, prefix="", is_last=True, is_root=False):
        items = list(node.items())
        if not items:  # Handle empty node edge case
            return
            
        if not is_root:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{items[0][0]}")
            prefix += "    " if is_last else "│   "
            items = items[1:]
        
        count = len(items)
        for i, (name, subtree) in enumerate(items):
            is_directory = subtree is not None and isinstance(subtree, dict)
            is_last_item = (i == count - 1)
            
            if is_directory:
                connector = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{connector}{name}/")
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                subdir_items = list(subtree.items())
                for j, (subname, subsubtree) in enumerate(subdir_items):
                    is_last_subitem = (j == len(subdir_items) - 1)
                    if subsubtree is None:  # File
                        lines.append(f"{new_prefix}{'└── ' if is_last_subitem else '├── '}{subname}")
                    else:  # Directory
                        print_tree(
                            {subname: subsubtree}, 
                            new_prefix, 
                            is_last=is_last_subitem,
                            is_root=True
                        )
            else:  # File
                connector = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{connector}{name}")
    
    # Start the tree from the root
    print_tree(tree, is_root=True)
    lines.append("```")
    
    return "\n".join(lines)

def process_with_content_helpers(input_dir: str, output_filename: str, mode: str, report_filename: str,
                                scan_extensions: set[str], scan_ignore_patterns: list[str], 
                                scan_use_gitignore: bool, policy_filter: bool):
    """
    Process a directory using specialized content helpers based on mode.
    
    This function coordinates the entire optimization process:
    1. Scan the directory for files matching criteria
    2. Initialize the appropriate content helper
    3. Process each file with the helper
    4. Write optimized content and generate report
    
    Args:
        input_dir: Path to input directory
        output_filename: Path for output file
        mode: Optimization mode (docs, code, notion, email, markdown, auto)
        report_filename: Path for report file
        scan_extensions: Set of file extensions to include
        scan_ignore_patterns: List of glob patterns to ignore
        scan_use_gitignore: Whether to respect .gitignore rules
        policy_filter: Whether to filter policy pages
    """
    start_time = time.time()
    processing_warnings = []
    original_chars = 0
    optimized_chars = 0
    original_tokens = -1
    optimized_tokens = -1
    files_processed = 0
    files_skipped = 0
    policy_pages_skipped = 0
    policy_pages_list = []

    print_header(f"Starting Content Optimization")
    print_info(f"Mode: {mode}, Input: {input_dir}")
    print_info(f"Output: {output_filename}, Report: {report_filename}")

    # Scan directory for files
    try:
        file_paths, files_skipped_scan = scan_directory(
            input_dir, scan_extensions, scan_ignore_patterns, scan_use_gitignore, processing_warnings
        )
        files_skipped += files_skipped_scan
    except Exception as e:
        error_msg = f"Directory scan failed: {str(e)}"
        print_error(error_msg)
        processing_warnings.append(error_msg)
        # Generate minimal report with error info and exit
        report_stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "input_source": input_dir,
            "source_type": "Directory Scan",
            "output_file": output_filename,
            "processing_time": time.time() - start_time,
            "warnings": [error_msg],
            "error": error_msg
        }
        try:
            generate_report(report_filename, report_stats)
        except:
            pass  # Last resort - if even report generation fails
        return

    if not file_paths:
        print_warning("No processable files found matching the criteria.")
        processing_warnings.append("No processable files found matching the criteria.")
        # Generate empty report and exit
        report_stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "input_source": input_dir,
            "source_type": "Directory Scan",
            "output_file": output_filename,
            "files_processed": 0,
            "files_skipped": files_skipped,
            "processing_time": time.time() - start_time,
            "warnings": processing_warnings
        }
        generate_report(report_filename, report_stats)
        return

    # Initialize appropriate helper based on mode
    try:
        if mode == "auto":
            print_info("Using auto-detection mode to process files")
            optimizer = get_unified_optimizer(default_mode="docs")
        else:
            print_info(f"Using {mode} mode to process all files")
            try:
                helper_class = get_content_helper(mode)
            except ValueError:
                print_error(f"Invalid mode: {mode}. Using docs mode as fallback.")
                helper_class = get_content_helper("docs")
                mode = "docs"
                processing_warnings.append(f"Invalid mode '{mode}'. Fell back to 'docs' mode.")
    except Exception as e:
        error_msg = f"Failed to initialize content helper: {str(e)}"
        print_error(error_msg)
        processing_warnings.append(error_msg)
        report_stats = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "input_source": input_dir,
            "source_type": "Directory Scan",
            "output_file": output_filename,
            "processing_time": time.time() - start_time,
            "warnings": processing_warnings,
            "error": error_msg
        }
        generate_report(report_filename, report_stats)
        return

    # Process the files
    print_header(f"Optimizing {len(file_paths)} Files")
    processed_content_sections = []
    processed_content_sections.append(OPTIMIZED_HEADER_FORMAT.format(mode=mode.upper(), source_type="Directory"))
    processed_content_sections.append(OPTIMIZED_SECTION_SEPARATOR)

    # Add directory structure
    try:
        dir_structure = generate_directory_tree(file_paths, clean_notion_ids=(mode == "notion"))
        if dir_structure:  # Make sure we have a valid directory structure
            processed_content_sections.append("# Directory Structure")
            processed_content_sections.append(dir_structure)
            processed_content_sections.append(OPTIMIZED_SECTION_SEPARATOR)
            processed_content_sections.append("# Files")
            processed_content_sections.append(OPTIMIZED_SECTION_SEPARATOR)
        else:
            # Add a placeholder if directory structure generation failed
            processed_content_sections.append("# Files")
            processed_content_sections.append(OPTIMIZED_SECTION_SEPARATOR)
    except Exception as e:
        processing_warnings.append(f"Failed to generate directory tree: {str(e)}")
        print_warning(f"Failed to generate directory tree: {e}")
        # Add fallback sections
        processed_content_sections.append("# Files")
        processed_content_sections.append(OPTIMIZED_SECTION_SEPARATOR)
        # Continue processing even if directory tree generation fails

    # Set up tracking for original content to calculate tokens
    all_original_content = ""
    aggregated_stats = defaultdict(int)
    detected_types = defaultdict(int)

    # Process each file
    progress_bar = tqdm(file_paths, desc="Optimizing files", unit="file") if TQDM_AVAILABLE else file_paths
    for rel_path in progress_bar:
        if TQDM_AVAILABLE:
            progress_bar.set_description(f"Optimizing {rel_path}")
        
        # Skip None values in file paths
        if rel_path is None:
            continue
            
        file_path = os.path.join(input_dir, rel_path)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            
            # Check policy filtering
            if policy_filter and hasattr(rules, 'is_policy_page') and rules.is_policy_page(rel_path, file_content):
                processing_warnings.append(f"Skipped policy page: {rel_path}")
                policy_pages_skipped += 1
                policy_pages_list.append(rel_path)
                files_skipped += 1
                continue

            # Track original content
            current_original_chars = len(file_content)
            original_chars += current_original_chars
            all_original_content += file_content + "\n\n"  # For token calculation

            # Process with appropriate helper
            try:
                if mode == "auto":
                    optimized_content, stats = optimizer.optimize_file(file_path, file_content)
                    if "detection" in stats and "type" in stats["detection"]:
                        detected_types[stats["detection"]["type"]] += 1
                else:
                    helper = helper_class()
                    optimized_content, stats = helper.process_file(file_path, file_content)

                # Update aggregated stats
                for stat_name, count in stats.items():
                    if isinstance(count, (int, float)):
                        aggregated_stats[stat_name] += count

                # Add to processed content - ensure no None values
                if optimized_content is not None:
                    processed_content_sections.append(OPTIMIZED_FILE_SEPARATOR_FORMAT.format(file_path=rel_path))
                    processed_content_sections.append(optimized_content)
                else:
                    processed_content_sections.append(OPTIMIZED_FILE_SEPARATOR_FORMAT.format(file_path=rel_path))
                    processed_content_sections.append("Content optimization failed - empty or invalid result")
                    processing_warnings.append(f"Empty or invalid result for {rel_path}")
                files_processed += 1
            except Exception as e:
                error_msg = f"Helper processing error on {rel_path}: {e}"
                print_warning(error_msg)
                processing_warnings.append(error_msg)
                # Add original content to preserve the file in output
                processed_content_sections.append(OPTIMIZED_FILE_SEPARATOR_FORMAT.format(file_path=rel_path))
                processed_content_sections.append(file_content)
                files_processed += 1  # Still count it as processed

        except Exception as e:
            error_msg = f"Error processing {rel_path}: {e}"
            print_warning(error_msg)
            processing_warnings.append(error_msg)
            files_skipped += 1
    
    if TQDM_AVAILABLE:
        progress_bar.close()

    # Calculate original tokens if tiktoken is available
    if TIKTOKEN_AVAILABLE and all_original_content:
        try:
            original_tokens = count_tokens(all_original_content)
        except Exception as e:
            print_warning(f"Token counting failed: {e}")
            processing_warnings.append(f"Token counting failed: {e}")
            original_tokens = -1

    # Assemble final output - filter out None values
    processed_content_sections = [section for section in processed_content_sections if section is not None]
    final_output = "\n\n".join(processed_content_sections)
    optimized_chars = len(final_output)
    
    # Calculate optimized tokens
    if TIKTOKEN_AVAILABLE and original_tokens > -1:
        try:
            optimized_tokens = count_tokens(final_output)
        except Exception as e:
            print_warning(f"Token counting failed: {e}")
            processing_warnings.append(f"Token counting failed: {e}")
            optimized_tokens = -1

    # Calculate reductions
    char_reduction = -1.0
    if original_chars > 0:
        char_reduction = ((original_chars - optimized_chars) / original_chars) * 100
        # Handle the case where optimization actually increased size
        if char_reduction < 0:
            print_warning(f"Character count increased by {abs(char_reduction):.2f}% after optimization")
            char_reduction = -1.0  # Reset to -1 to indicate no reduction in reporting
    
    token_reduction = -1.0
    if original_tokens > 0 and optimized_tokens > -1:
        token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100
        # Handle the case where optimization increased token count
        if token_reduction < 0:
            print_warning(f"Token count increased by {abs(token_reduction):.2f}% after optimization")
            token_reduction = -1.0  # Reset to -1 to indicate no reduction in reporting

    # Write output file
    print_header("Writing Output")
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print_info(f"Created output directory: {output_dir}")
        
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            f_out.write(final_output)
        print_success(f"Optimized content written to: {output_filename}")
    except Exception as e:
        print_error(f"Failed to write output file: {e}")
        processing_warnings.append(f"Output file write error: {e}")

    # Print statistics
    print_header("Optimization Statistics")
    print_info(f"Original Size: {format_stat(original_chars)} chars, {format_stat(original_tokens)} tokens")
    print_info(f"Optimized Size: {format_stat(optimized_chars)} chars, {format_stat(optimized_tokens)} tokens")
    
    if char_reduction > 0:
        print_success(f"Character Reduction: {char_reduction:.2f}%")
    elif optimized_chars > original_chars:
        print_warning(f"Character Count Increased: {((optimized_chars - original_chars) / original_chars) * 100:.2f}%")
    else:
        print_info("Character Reduction: N/A")
    
    if token_reduction > 0:
        print_success(f"Token Reduction: {token_reduction:.2f}%")
    elif optimized_tokens > original_tokens:
        print_warning(f"Token Count Increased: {((optimized_tokens - original_tokens) / original_tokens) * 100:.2f}%")
    else:
        print_info("Token Reduction: N/A")
    
    print_success(f"Files Processed: {files_processed}")
    if files_skipped > 0:
        print_info(f"Files Skipped: {files_skipped}")
    if policy_pages_skipped > 0:
        print_info(f"Policy Pages Skipped: {policy_pages_skipped}")
    
    processing_time = time.time() - start_time
    print_success(f"Optimization complete in {processing_time:.2f} seconds")

    # Generate report
    report_stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "input_source": input_dir,
        "source_type": "Directory Scan",
        "output_file": output_filename,
        "original_chars": original_chars,
        "optimized_chars": optimized_chars,
        "char_reduction": char_reduction,
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "token_reduction": token_reduction,
        "files_processed": files_processed,
        "files_skipped": files_skipped,
        "policy_pages_skipped": policy_pages_skipped,
        "policy_pages_list": policy_pages_list,
        "policy_filter_enabled": policy_filter,
        "processing_time": processing_time,
        "warnings": processing_warnings,
        "scan_extensions": ','.join(sorted(list(scan_extensions))),
        "scan_ignore_patterns": scan_ignore_patterns,
        "scan_use_gitignore": scan_use_gitignore,
        "detected_types": dict(detected_types),
        "aggregated_stats": dict(aggregated_stats)
    }
    
    try:
        generate_report(report_filename, report_stats)
        print_success(f"Report generated: {report_filename}")
    except Exception as e:
        print_error(f"Failed to generate report: {e}")
        processing_warnings.append(f"Report generation error: {e}")

def generate_report(report_filename: str, stats: dict):
    """
    Generates a detailed markdown report file summarizing the optimization run.
    """
    # Ensure report directory exists
    report_dir = os.path.dirname(report_filename)
    if report_dir and not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        # Header
        f.write("# Content Optimization Report\n\n")
        f.write(f"**Run Timestamp:** {stats.get('timestamp', 'N/A')}\n")
        f.write(f"**Optimization Mode:** `{stats.get('mode', 'N/A')}`\n")
        f.write(f"**Input Source:** `{stats.get('input_source', 'N/A')}`\n\n")
        
        # Output file info
        f.write("## Output File\n")
        f.write(f"- **Output Path:** `{stats.get('output_file', 'N/A')}`\n\n")
        
        # Scan configuration
        f.write("## Scan Configuration\n")
        f.write(f"- **Included Extensions:** `{stats.get('scan_extensions', 'N/A')}`\n")
        ignore_pats = stats.get('scan_ignore_patterns', [])
        ignore_pats_str = ', '.join(f"`{p}`" for p in ignore_pats) if ignore_pats else 'None'
        f.write(f"- **Ignored Patterns:** {ignore_pats_str}\n")
        f.write(f"- **Used .gitignore:** {'Yes' if stats.get('scan_use_gitignore', False) else 'No'}\n\n")
        
        # Content type detection results (if auto mode)
        if stats.get('mode') == 'auto' and stats.get('detected_types'):
            f.write("## Content Type Detection\n")
            f.write("| Content Type | Files |\n")
            f.write("|-------------|------:|\n")
            for content_type, count in sorted(stats.get('detected_types', {}).items()):
                f.write(f"| {content_type} | {count} |\n")
            f.write("\n")
        
        # Overall statistics
        f.write("## Optimization Statistics\n")
        f.write("| Metric | Original | Optimized | Reduction |\n")
        f.write("|--------|----------|-----------|----------|\n")
        f.write(f"| Character Count | {format_stat(stats.get('original_chars', 0))} | {format_stat(stats.get('optimized_chars', 0))} | {format_stat(stats.get('char_reduction', -1))} |\n")
        f.write(f"| Token Count | {format_stat(stats.get('original_tokens', -1))} | {format_stat(stats.get('optimized_tokens', -1))} | {format_stat(stats.get('token_reduction', -1))} |\n")
        f.write(f"| Files Processed | {stats.get('files_processed', 0)} | | |\n")
        if stats.get('files_skipped', 0) > 0:
            f.write(f"| Files Skipped | {stats.get('files_skipped', 0)} | | |\n")
        f.write(f"| Processing Time | {stats.get('processing_time', 0):.2f} seconds | | |\n\n")
        
        # Optimizations applied
        f.write("## Optimizations Applied\n")
        
        # Summary text
        files_processed = stats.get('files_processed', 0)
        f.write(f"- Processed **{files_processed}** files\n")
        
        if stats.get('char_reduction', -1) > 0:
            chars_removed = stats.get('original_chars', 0) - stats.get('optimized_chars', 0)
            f.write(f"- Removed **{chars_removed:,}** characters, reducing content size by {format_stat(stats.get('char_reduction', 0))}.\n")
        
        if stats.get('token_reduction', -1) > 0:
            tokens_removed = stats.get('original_tokens', 0) - stats.get('optimized_tokens', 0)
            f.write(f"- Reduced token count by **{tokens_removed:,}** tokens ({format_stat(stats.get('token_reduction', 0))}).\n")
        
        # Show aggregated optimization stats
        aggregated_stats = stats.get('aggregated_stats', {})
        if aggregated_stats:
            f.write("\n### Optimization Actions\n")
            f.write("| Action | Count |\n")
            f.write("|--------|------:|\n")
            for action, count in sorted(aggregated_stats.items()):
                if isinstance(count, (int, float)) and count > 0:
                    f.write(f"| {action} | {count:,} |\n")
            f.write("\n")
        
        # Warnings section
        f.write("## Warnings and Issues\n")
        warnings_list = stats.get('warnings', [])
        if warnings_list:
            for warning in warnings_list:
                f.write(f"- `{warning}`\n")
        else:
            f.write("None\n")
        
        # Conclusion
        f.write("\n## Conclusion\n")
        conclusion = f"Content optimization completed successfully, processing {files_processed} files"
        if stats.get('char_reduction', -1) > 0:
            conclusion += f" with a {format_stat(stats.get('char_reduction', 0))} reduction in content size"
        if stats.get('token_reduction', -1) > 0:
            conclusion += f" and {format_stat(stats.get('token_reduction', 0))} reduction in tokens"
        conclusion += "."
        f.write(conclusion)

def main():
    """Parses command-line arguments and initiates the optimization process."""
    # Ensure quick script is executable
    quick_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimize-quick.sh")
    if os.path.exists(quick_script_path) and not os.access(quick_script_path, os.X_OK):
        try:
            os.chmod(quick_script_path, 0o755)
            print_info(f"Made optimize-quick.sh executable")
        except Exception as e:
            print_warning(f"Could not make optimize-quick.sh executable: {e}")
    
    parser = argparse.ArgumentParser(
        description="Optimize text content for LLM consumption by removing noise and boilerplate.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Input source arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-d", "--input_dir", help="Path to the root directory of the content to scan.")
    input_group.add_argument("-i", "--input_file", help="Path to the input file (e.g., a Repomix file).")
    input_group.add_argument("-q", "--quick", help="Quick optimization with sensible defaults (docs mode)", metavar="DIR")
    input_group.add_argument("-n", "--notion", help="Process a Notion.so export directory with specialized handling", metavar="DIR")
    input_group.add_argument("-a", "--auto", help="Auto-detect content types for optimal processing", metavar="DIR")

    # Output and configuration
    parser.add_argument("-o", "--output_file", default=None,
                        help="Path for the optimized output file. If omitted, generated automatically.")
    parser.add_argument("-m", "--mode", choices=SUPPORTED_MODES, default=DEFAULT_MODE,
                        help="Optimization mode. Use 'auto' for content type detection.")
    parser.add_argument("--report_file", default=None,
                        help="Path for the optimization report file.")

    # Directory scanning options
    dir_group = parser.add_argument_group('Directory Scanning Options')
    dir_group.add_argument("--extensions", default=DEFAULT_SCAN_EXTENSIONS,
                          help="Comma-separated list of file extensions to include.")
    dir_group.add_argument("--ignore", default=DEFAULT_IGNORE_PATTERNS,
                          help="Comma-separated list of glob patterns to ignore.")
    dir_group.add_argument("--use-gitignore", action='store_true', default=False,
                          help="Respect .gitignore rules during scanning.")

    # Filtering arguments
    policy_filter_group = parser.add_mutually_exclusive_group()
    policy_filter_group.add_argument("--policy-filter", action='store_true', dest='policy_filter', default=DEFAULT_POLICY_FILTER,
                                    help="Enable filtering of potential policy pages (default).")
    policy_filter_group.add_argument("--no-policy-filter", action='store_false', dest='policy_filter',
                                    help="Disable filtering of policy pages (process all files).")

    args = parser.parse_args()

    # Check for core dependencies
    if not CONTENT_HELPERS_AVAILABLE:
        print_error("Required content_helpers module not found. Please check your installation.")
        return 1

    # Process quick mode shortcut
    if args.quick:
        args.input_dir = args.quick
        args.mode = 'docs'
        print_info("Quick mode activated: Using docs mode with default settings")
    
    # Process notion mode shortcut
    if args.notion:
        args.input_dir = args.notion
        args.mode = 'notion'
        print_info("Notion mode activated: Using specialized settings for Notion exports")
    
    # Process auto mode shortcut
    if args.auto:
        args.input_dir = args.auto
        args.mode = 'auto'
        print_info("Auto-detect mode activated: Will analyze each file for optimal processing")

    # Process extensions into a set
    scan_extensions_set = {ext.strip().lower() if ext.strip().startswith('.') else '.' + ext.strip().lower()
                          for ext in args.extensions.split(',') if ext.strip()}

    # Process ignore patterns
    raw_ignore_patterns = [pat.strip() for pat in args.ignore.split(',') if pat.strip()]
    scan_ignore_patterns = []
    
    # Add trailing slash to common directory names for better ignoring
    common_dirs = {'.git', '.hg', '.svn', 'build', 'dist', 'node_modules', '__pycache__', '.vscode', '.idea', '.venv', 'venv'}
    for pat in raw_ignore_patterns:
        is_simple_dir = pat in common_dirs and '/' not in pat and '*' not in pat and '?' not in pat and '[' not in pat
        if is_simple_dir:
            scan_ignore_patterns.append(pat + '/')
        scan_ignore_patterns.append(pat)
    
    # Remove duplicates and sort
    scan_ignore_patterns = sorted(list(set(scan_ignore_patterns)))

    # Calculate paths
    if args.input_dir:
        input_source = args.input_dir
        is_directory = True
        
        # Validate directory
        input_path = Path(input_source)
        if not input_path.is_dir():
            print_error(f"Input directory '{input_source}' not found or not a directory.")
            return 1
        
    elif args.input_file:
        input_source = args.input_file
        is_directory = False
        
        # Validate file
        input_path = Path(input_source)
        if not input_path.is_file():
            print_error(f"Input file '{input_source}' not found or not a file.")
            return 1
    else:
        print_error("No input source specified.")
        return 1

    # Generate output filename if not provided
    if args.output_file:
        output_filename = args.output_file
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if is_directory:
            base_name = input_path.resolve().name
            output_filename = f"{base_name}-optimized-{args.mode}-{ts}.md"
        else:
            base = input_path.stem
            output_ext = '.md'
            if input_path.suffix and input_path.suffix.lower() not in ['.txt', '.md', '.markdown']:
                output_ext = input_path.suffix
            output_filename = f"{base}-optimized-{args.mode}{output_ext}"

    # Generate report filename if not provided
    if args.report_file:
        report_filename = args.report_file
    else:
        output_base, _ = os.path.splitext(output_filename)
        report_filename = f"{output_base}-report.md"

    # Check availability of optional dependencies
    if args.use_gitignore and not GITIGNORE_AVAILABLE:
        print_warning("Warning: --use-gitignore specified, but 'gitignore-parser' package is not installed.")

    if is_directory:
        # Process directory using specialized helpers
        process_with_content_helpers(
            input_dir=input_source,
            output_filename=output_filename,
            mode=args.mode,
            report_filename=report_filename,
            scan_extensions=scan_extensions_set,
            scan_ignore_patterns=scan_ignore_patterns,
            scan_use_gitignore=args.use_gitignore,
            policy_filter=args.policy_filter
        )
    else:
        # For Repomix file processing, we keep using the classic approach
        # This section could be updated in the future to use specialized helpers
        print_error("Repomix file processing is not yet supported with the new content helpers.")
        return 1

    return 0

if __name__ == "__main__":
    try:
        print(f"\n{BOLD}{MAGENTA}Content Optimizer{RESET} {BLUE}v{VERSION}{RESET}")
        print(f"{CYAN}Optimizing content for LLM consumption{RESET}\n")
        
        exit_code = main()
        sys.exit(exit_code)
    except SystemExit as e:
        sys.exit(e.code or 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Operation cancelled by user.{RESET}", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n{BOLD}{RED}--- UNEXPECTED ERROR ---{RESET}", file=sys.stderr)
        print(f"{RED}An unhandled error occurred: {type(e).__name__}: {e}{RESET}", file=sys.stderr)
        traceback.print_exc()
        print(f"{BOLD}{RED}------------------------{RESET}", file=sys.stderr)
        sys.exit(1)