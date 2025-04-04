#!/bin/bash
# Utility script to test and apply duplicate content removal

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

# Make the script executable
chmod +x "$0"

print_header "Duplicate Content Remover Utility"
print_info "This script will optimize a file or directory, focusing on removing duplicate headings and forms."

# Check if a parameter was provided
if [ -z "$1" ]; then
  print_warning "No input specified. Usage: ./fix-duplicate-content.sh [file or directory]"
  exit 1
fi

# Process the input
if [ -d "$1" ]; then
  print_info "Processing directory: $1"
  python3 optimize.py -d "$1" -m docs --extensions .md,.txt,.html
elif [ -f "$1" ]; then
  print_info "Processing file: $1"
  python3 optimize.py -i "$1" -m docs
else
  print_warning "Input '$1' is not a valid file or directory"
  exit 1
fi

print_success "Processing complete. Check the output file for results."
