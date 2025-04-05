#!/bin/bash
# Script to convert .mdc files to .md files in a directory

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RED="\033[0;31m"
BOLD="\033[1m"
RESET="\033[0m"

# Make the script executable
chmod +x "$0"
chmod +x convert_mdc_to_md.py

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

print_error() {
  echo -e "${RED}✗ $1${RESET}"
}

show_help() {
  print_header "Convert .mdc Files to .md Files"
  echo "Usage: ./convert-mdc-to-md.sh [options] <directory>"
  echo
  echo "Options:"
  echo "  -h, --help          Show this help message"
  echo "  -d, --dry-run       Show what would be done without making changes"
  echo "  -r, --remove        Remove original .mdc files after conversion"
  echo
  echo "Examples:"
  echo "  ./convert-mdc-to-md.sh ./rules              # Convert files in rules directory"
  echo "  ./convert-mdc-to-md.sh -d ./rules           # Dry run in rules directory"
  echo "  ./convert-mdc-to-md.sh -r ./rules           # Convert and remove originals"
  echo
}

# Default values
DRY_RUN=false
REMOVE_ORIGINALS=false
DIRECTORY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -d|--dry-run)
      DRY_RUN=true
      shift
      ;;
    -r|--remove)
      REMOVE_ORIGINALS=true
      shift
      ;;
    *)
      DIRECTORY="$1"
      shift
      ;;
  esac
done

# Check if directory is provided
if [ -z "$DIRECTORY" ]; then
  print_error "No directory specified"
  show_help
  exit 1
fi

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
  print_error "Directory '$DIRECTORY' does not exist"
  exit 1
fi

# Build command
CMD="./convert_mdc_to_md.py"
if [ "$DRY_RUN" = true ]; then
  CMD="$CMD --dry-run"
fi
if [ "$REMOVE_ORIGINALS" = true ]; then
  CMD="$CMD --remove-originals"
fi
CMD="$CMD \"$DIRECTORY\""

# Run the conversion
print_header "Converting .mdc Files to .md Files"
print_info "Directory: $DIRECTORY"
print_info "Dry run: $DRY_RUN"
print_info "Remove originals: $REMOVE_ORIGINALS"
print_info "Running command: $CMD"
echo

eval $CMD

exit_status=$?
if [ $exit_status -eq 0 ]; then
  print_success "Conversion completed successfully"
else
  print_error "Conversion failed with exit code $exit_status"
fi

exit $exit_status
