#!/bin/bash
# Utility script to generate an enhanced report for previously optimized content

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

print_error() {
  echo -e "${RED}✗ $1${RESET}"
}

# Make the script executable
chmod +x "$0"

print_header "Enhanced Report Generator"
print_info "This script generates an improved report for previously optimized content"

# Check if a parameter was provided
if [ -z "$1" ]; then
  print_warning "No input specified. Usage: ./generate-enhanced-report.sh [optimized-file] [original-file (optional)]"
  exit 1
fi

OPTIMIZED_FILE="$1"
ORIGINAL_FILE="$2"
OUTPUT_REPORT="${OPTIMIZED_FILE%.*}-enhanced-report.md"

if [ ! -f "$OPTIMIZED_FILE" ]; then
  print_error "Optimized file not found: $OPTIMIZED_FILE"
  exit 1
fi

ORIGINAL_CHARS=0
OPTIMIZED_CHARS=$(wc -c < "$OPTIMIZED_FILE")

if [ -n "$ORIGINAL_FILE" ] && [ -f "$ORIGINAL_FILE" ]; then
  print_info "Using original file for comparison: $ORIGINAL_FILE"
  ORIGINAL_CHARS=$(wc -c < "$ORIGINAL_FILE")
else
  print_info "No original file specified. Basic report will be generated."
fi

print_info "Generating enhanced report..."

python3 -c "
import sys
sys.path.append('.')
try:
    from report_generator import generate_report
    
    # Prepare stats dictionary
    stats = {
        'timestamp': 'Post-processing analysis',
        'mode': 'post-analysis',
        'input_source': '$ORIGINAL_FILE',
        'source_type': 'File Analysis',
        'output_file': '$OPTIMIZED_FILE',
        'original_chars': $ORIGINAL_CHARS,
        'optimized_chars': $OPTIMIZED_CHARS,
    }
    
    # Calculate reduction if we have both files
    if $ORIGINAL_CHARS > 0 and $OPTIMIZED_CHARS > 0:
        stats['char_reduction'] = (($ORIGINAL_CHARS - $OPTIMIZED_CHARS) / $ORIGINAL_CHARS) * 100
    else:
        stats['char_reduction'] = -1
    
    # Generate the report
    success = generate_report('$OUTPUT_REPORT', stats)
    if success:
        print('Report generated successfully: $OUTPUT_REPORT')
    else:
        print('Error generating report')
        sys.exit(1)
except ImportError:
    print('Error: report_generator module not found')
    sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
  print_success "Enhanced report generated: $OUTPUT_REPORT"
else
  print_error "Failed to generate enhanced report"
  exit 1
fi
