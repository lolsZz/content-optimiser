#!/bin/bash
# Utility script to target and remove the Erdington Baths subscription form

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

print_header "Erdington Baths Form Removal Utility"
print_info "This script will process a specific file to remove the Erdington Baths subscription form."

# Check if a parameter was provided
if [ -z "$1" ]; then
  print_warning "No input specified. Usage: ./fix-specific-form.sh [file]"
  exit 1
fi

# Process the input
if [ -f "$1" ]; then
  print_info "Processing file: $1"
  OUTPUT_FILE="${1%.*}-fixed.${1##*.}"
  python3 -c "
import re

pattern = re.compile(
    r'/\\s*\\n'
    r'If you would like to be kept updated on the progress of the transformation of Erdington Baths.*?\\n\\n'
    r'We are thrilled to have you join our community.*?\\n\\n'
    r'## Subscribe for Updates on Erdington Enterprise Hub\\n\\n'
    r'- indicates required\\n\\n'
    r'First Name\\n\\n'
    r'Last Name\\n\\n'
    r'Email Address \\*\\n\\n'
    r'/\\* real people should not fill this in.*?\\*/',
    re.MULTILINE | re.DOTALL
)

replacement = '## Updates on Erdington Enterprise Hub'

with open('$1', 'r', encoding='utf-8') as f:
    content = f.read()

fixed_content = pattern.sub(replacement, content)

with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

matches = len(pattern.findall(content))
print(f'Replaced {matches} instances of the subscription form.')
  "
  print_success "Processing complete. Check the output file: $OUTPUT_FILE"
else
  print_warning "Input '$1' is not a valid file"
  exit 1
fi
