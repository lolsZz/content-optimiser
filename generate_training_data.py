#!/usr/bin/env python3
"""
LLM Training Data Generator CLI

This script provides a command-line interface for generating training data
for Large Language Models (LLMs) from optimized content from Content Optimizer.

It transforms optimized content into various training data formats suitable
for different LLM training approaches.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
import glob

try:
    from llm_training_generator import (
        LLMTrainingDataGenerator,
        FORMAT_INSTRUCTION,
        FORMAT_CONVERSATION,
        FORMAT_COMPLETION,
        FORMAT_QA,
        FORMAT_GENERAL,
        OUTPUT_JSONL,
        OUTPUT_CSV,
        OUTPUT_PARQUET,
        OUTPUT_HF_DATASET,
        SUPPORTED_FORMATS,
        SUPPORTED_OUTPUT_FORMATS
    )
except ImportError:
    print("Error: LLM Training Generator module not found. Make sure llm_training_generator.py is in the same directory.")
    sys.exit(1)

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
    term_width = min(os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80, 80)
    separator = "=" * term_width
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

def format_examples_count(count):
    """Format the examples count with comma separators"""
    return f"{count:,}"

def main():
    """
    Main entry point for the training data generation CLI.
    Parses command-line arguments and runs the generator.
    """
    parser = argparse.ArgumentParser(
        description="Generate training data for Large Language Models from optimized content.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input arguments
    parser.add_argument("-i", "--input", required=True,
                      help="Path to the optimized content file(s). Supports glob patterns.")
    
    # Output arguments
    parser.add_argument("-o", "--output_dir", default=None,
                      help="Directory to save generated training data. Defaults to same directory as input.")
    
    # Format arguments
    parser.add_argument("-f", "--format", choices=SUPPORTED_FORMATS, default=FORMAT_INSTRUCTION,
                      help="Training data format to generate.")
    parser.add_argument("--output_format", choices=SUPPORTED_OUTPUT_FORMATS, default=OUTPUT_JSONL,
                      help="Output file format for the training data.")
    
    # Generation options
    parser.add_argument("--max_examples", type=int, default=10000,
                      help="Maximum number of examples to generate per file.")
    parser.add_argument("--min_tokens", type=int, default=50,
                      help="Minimum token count for examples to include.")
    parser.add_argument("--max_tokens", type=int, default=1024,
                      help="Maximum token count for examples to include.")
    parser.add_argument("--no_metadata", action="store_true",
                      help="Exclude metadata from generated examples.")
    parser.add_argument("--seed", type=int, default=None,
                      help="Random seed for reproducible generation.")
    
    # Miscellaneous
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Enable verbose output.")
    parser.add_argument("-c", "--config", default=None,
                      help="Path to a JSON configuration file with generator settings.")
    parser.add_argument("--version", action="version", version="LLM Training Data Generator v1.0.0")
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        import random
        random.seed(args.seed)
    
    # Print banner
    print(f"\n{BOLD}{MAGENTA}LLM Training Data Generator{RESET} {BLUE}v1.0.0{RESET}")
    print(f"{CYAN}Generating training data for LLMs from optimized content{RESET}\n")
    
    # Load configuration if provided
    config = {}
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print_info(f"Loaded configuration from {args.config}")
        except Exception as e:
            print_warning(f"Failed to load configuration file: {e}")
    
    # Override config with command-line arguments
    config.update({
        "data_format": args.format,
        "output_format": args.output_format,
        "max_examples": args.max_examples,
        "min_token_count": args.min_tokens,
        "max_token_count": args.max_tokens,
        "include_metadata": not args.no_metadata,
        "verbose": args.verbose
    })
    
    # Initialize the generator
    generator = LLMTrainingDataGenerator(config)
    
    # Process input files
    input_files = glob.glob(args.input)
    
    if not input_files:
        print_error(f"No files found matching pattern: {args.input}")
        return 1
    
    print_header(f"Processing {len(input_files)} File(s)")
    
    total_examples = 0
    successful_files = 0
    
    for input_file in input_files:
        print_info(f"Processing file: {input_file}")
        
        try:
            # Generate training data
            output_file = generator.generate_from_file(input_file, args.output_dir)
            
            # Get statistics
            stats = generator.get_stats()
            examples_count = stats.get("examples_generated", 0) - stats.get("examples_filtered", 0)
            total_examples += examples_count
            
            print_success(f"Generated {format_examples_count(examples_count)} training examples -> {output_file}")
            successful_files += 1
            
            # Show additional stats
            if args.verbose:
                print_info(f"  • Average tokens per example: {stats.get('avg_tokens_per_example', 0):.1f}")
                print_info(f"  • Examples filtered out: {stats.get('examples_filtered', 0)}")
                
                # Data format breakdown
                format_stats = stats.get("data_formats", {})
                if format_stats:
                    print_info("  • Generated examples by format:")
                    for fmt, count in format_stats.items():
                        print_info(f"    - {fmt}: {count}")
        
        except Exception as e:
            print_error(f"Failed to process {input_file}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Show summary
    print_header("Generation Summary")
    print_info(f"Successfully processed {successful_files}/{len(input_files)} files")
    print_info(f"Total examples generated: {format_examples_count(total_examples)}")
    
    if args.output_dir:
        print_info(f"Output saved to: {args.output_dir}")
    
    print_success("Training data generation complete!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Operation cancelled by user.{RESET}", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n{BOLD}{RED}--- UNEXPECTED ERROR ---{RESET}", file=sys.stderr)
        print(f"{RED}An unhandled error occurred: {type(e).__name__}: {e}{RESET}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        print(f"{BOLD}{RED}------------------------{RESET}", file=sys.stderr)
        sys.exit(1)
