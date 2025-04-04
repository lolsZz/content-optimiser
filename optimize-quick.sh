#!/bin/bash
# Make the script executable by default
chmod +x "$0"

# Quick launcher for Content Optimizer with simplified interface

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
BOLD="\033[1m"
RESET="\033[0m"

print_header() {
  echo -e "\n${BOLD}${BLUE}$1${RESET}\n"
}

print_info() {
  echo -e "${CYAN}$1${RESET}"
}

print_usage() {
  echo -e "${BOLD}${BLUE}Content Optimizer Quick Start${RESET}"
  echo
  echo -e "Usage: ${YELLOW}./optimize-quick.sh [option] <input>${RESET}"
  echo
  echo "Options:"
  echo -e "  ${GREEN}auto${RESET}    Auto-detect content types (recommended)"
  echo -e "  ${GREEN}docs${RESET}    Optimize documentation/web content"
  echo -e "  ${GREEN}code${RESET}    Optimize source code repositories"
  echo -e "  ${GREEN}notion${RESET}  Optimize Notion.so exports"
  echo -e "  ${GREEN}email${RESET}   Optimize email content"
  echo -e "  ${GREEN}markdown${RESET} Optimize Markdown/HTML content"
  echo -e "  ${GREEN}train${RESET}   Generate LLM training data from optimized content"
  echo -e "  ${GREEN}help${RESET}    Show this help message"
  echo
  echo "Examples:"
  echo -e "  ${YELLOW}./optimize-quick.sh auto ./mixed-content${RESET}"
  echo -e "  ${YELLOW}./optimize-quick.sh docs ./my-docs${RESET}"
  echo -e "  ${YELLOW}./optimize-quick.sh code ./my-repository${RESET}"
  echo -e "  ${YELLOW}./optimize-quick.sh notion ./my-notion-export${RESET}"
  echo -e "  ${YELLOW}./optimize-quick.sh email ./my-email-archive${RESET}"
  echo -e "  ${YELLOW}./optimize-quick.sh train ./optimized-content.md${RESET}"
  echo
}

# Check if Python and the optimizer script exist
if ! command -v python3 &> /dev/null; then
  echo -e "${YELLOW}Error: python3 is required but not found in PATH${RESET}" >&2
  exit 1
fi

if [ ! -f "optimize.py" ]; then
  echo -e "${YELLOW}Error: optimize.py not found in current directory${RESET}" >&2
  exit 1
fi

# Make sure the scripts are executable
chmod +x optimize.py
if [ -f "generate_training_data.py" ]; then
  chmod +x generate_training_data.py
fi

# Process arguments
if [ $# -lt 1 ] || [ "$1" = "help" ]; then
  print_usage
  exit 0
fi

MODE="auto"  # Default mode - use auto-detection
INPUT=""

if [ "$1" = "docs" ] || [ "$1" = "code" ] || [ "$1" = "notion" ] || [ "$1" = "email" ] || [ "$1" = "markdown" ] || [ "$1" = "auto" ] || [ "$1" = "train" ]; then
  MODE="$1"
  INPUT="$2"
else
  # Assume input only, use auto mode
  INPUT="$1"
fi

if [ -z "$INPUT" ]; then
  echo -e "${YELLOW}Error: No input specified${RESET}" >&2
  print_usage
  exit 1
fi

# Handle train mode separately
if [ "$MODE" = "train" ]; then
  if [ ! -f "generate_training_data.py" ]; then
    echo -e "${YELLOW}Error: generate_training_data.py not found in current directory${RESET}" >&2
    exit 1
  fi
  
  print_header "GENERATING LLM TRAINING DATA FROM: $INPUT"
  print_info "Using instruction format (default)"
  
  # Run the training data generator
  python3 generate_training_data.py -i "$INPUT" -f instruction
  exit $?
fi

# Determine if input is a directory or file
if [ -d "$INPUT" ]; then
  print_header "OPTIMIZING DIRECTORY: $INPUT"
  print_info "Running in $MODE mode..."
  
  # Use appropriate flag based on mode
  if [ "$MODE" = "notion" ]; then
    python3 optimize.py -n "$INPUT"
  elif [ "$MODE" = "auto" ]; then
    python3 optimize.py -a "$INPUT"
  else
    python3 optimize.py -d "$INPUT" -m "$MODE"
  fi
elif [ -f "$INPUT" ]; then
  print_header "OPTIMIZING FILE: $INPUT"
  print_info "Running in $MODE mode..."
  python3 optimize.py -i "$INPUT" -m "$MODE"
else
  echo -e "${YELLOW}Error: Input '$INPUT' is not a valid file or directory${RESET}" >&2
  exit 1
fi

exit 0
