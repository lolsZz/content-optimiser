#!/bin/bash
# Script to generate Amazon Q compatible training data from optimized code content

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RED="\033[0;31m"
BOLD="\033[1m"
RESET="\033[0m"

print_header() {
  echo -e "\n${BOLD}${BLUE}$1${RESET}\n"
}

print_info() {
  echo -e "${CYAN}ℹ $1${RESET}"
}

print_success() {
  echo -e "${GREEN}✓ $1${RESET}"
}

print_warning() {
  echo -e "${YELLOW}⚠️ $1${RESET}"
}

# Make the script executable by default
chmod +x "$0"

print_header "Amazon Q Training Data Generator"
print_info "This script generates Amazon Q compatible completion training data"

# Check if input file is provided
if [ -z "$1" ]; then
  print_warning "No input specified. Usage: ./generate-amazonq-training-data.sh [optimized-code-file]"
  exit 1
fi

INPUT_FILE="$1"
CONFIG_FILE="./amazonq-completion-specs.json"
OUTPUT_DIR="./amazonq-training-data"

# Verify input file exists
if [ ! -f "$INPUT_FILE" ]; then
  print_warning "Input file not found: $INPUT_FILE"
  exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

print_info "Processing: $INPUT_FILE"
print_info "Using configuration: $CONFIG_FILE"
print_info "Output directory: $OUTPUT_DIR"

# Generate the training data with specific Amazon Q parameters
python3 ../generate_training_data.py \
  -i "$INPUT_FILE" \
  -f completion \
  --min_tokens 30 \
  --max_tokens 512 \
  -o "$OUTPUT_DIR" \
  --output_format jsonl \
  -c "$CONFIG_FILE"

print_success "Amazon Q training data generation complete!"
print_info "Check output in: $OUTPUT_DIR"
