#!/bin/bash
# A utility script to diagnose and fix optimization issues

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

print_warning() {
  echo -e "${YELLOW}⚠️ $1${RESET}"
}

print_error() {
  echo -e "${RED}✗ $1${RESET}"
}

print_success() {
  echo -e "${GREEN}✓ $1${RESET}"
}

# Make sure the script is executable
chmod +x "$0"

print_header "Content Optimizer Diagnostics"

# Check Python environment
print_info "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
  print_error "Python 3 is not installed or not in PATH"
  exit 1
fi

# Check required files
print_info "Checking required files..."
MISSING_FILES=0
for file in optimize.py optimization_rules.py content_helpers/__init__.py content_helpers/base_helper.py content_helpers/unified_optimizer.py; do
  if [ ! -f "$file" ]; then
    print_error "Missing required file: $file"
    MISSING_FILES=$((MISSING_FILES + 1))
  fi
done

if [ $MISSING_FILES -gt 0 ]; then
  print_error "Missing $MISSING_FILES required files. Please reinstall the package."
  exit 1
fi

# Check dependencies
print_info "Checking dependencies..."
python3 -c "
try:
    import tiktoken
    print('✓ tiktoken is installed')
except ImportError:
    print('⚠️ tiktoken is not installed (token counting will be unavailable)')

try:
    import pygments
    print('✓ pygments is installed')
except ImportError:
    print('⚠️ pygments is not installed (code detection will be limited)')

try:
    import tqdm
    print('✓ tqdm is installed')
except ImportError:
    print('⚠️ tqdm is not installed (progress bars will be unavailable)')

try:
    import gitignore_parser
    print('✓ gitignore-parser is installed')
except ImportError:
    print('⚠️ gitignore-parser is not installed (.gitignore support will be unavailable)')
"

# Check for common issues
print_header "Checking For Common Issues"

# Check file permissions
print_info "Checking file permissions..."
if [ ! -x "optimize.py" ]; then
  print_warning "optimize.py is not executable"
  chmod +x optimize.py
  print_success "Fixed permissions for optimize.py"
fi

if [ ! -x "optimize-quick.sh" ]; then
  print_warning "optimize-quick.sh is not executable"
  chmod +x optimize-quick.sh
  print_success "Fixed permissions for optimize-quick.sh"
fi

# Perform diagnostic test run
print_header "Running Diagnostic Test"
print_info "This will create a test file and run a diagnostic optimization"

# Create a test file with known content
mkdir -p test_content
cat > test_content/test_file.md << 'EOF'
# Test Document

This is a simple test document for the Content Optimizer.

## Navigation Menu

Home
About
Products
Services
Contact

## Main Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt 
ut labore et dolore magna aliqua.

```python
def hello_world():
    print("Hello, World!")
```

## Contact Form

Send Message

Name: _________________

Email: _________________

Message: _________________

Submit
EOF

# Run optimization in diagnostic mode
print_info "Running diagnostic optimization..."
python3 optimize.py -d test_content -m docs -o test_content/optimized_test.md

# Check results
if [ -f "test_content/optimized_test.md" ]; then
  ORIGINAL_SIZE=$(wc -c < test_content/test_file.md)
  OPTIMIZED_SIZE=$(wc -c < test_content/optimized_test.md)
  
  if [ "$OPTIMIZED_SIZE" -lt "$ORIGINAL_SIZE" ]; then
    print_success "Optimization successful: reduced size from $ORIGINAL_SIZE to $OPTIMIZED_SIZE bytes"
  else
    print_warning "Optimization did not reduce size: $ORIGINAL_SIZE -> $OPTIMIZED_SIZE bytes"
  fi
else
  print_error "Optimization failed: output file not created"
fi

print_header "Recommendations"
echo -e "If you're still experiencing issues with size increases after optimization:"
echo
echo -e "1. ${BOLD}Check your content:${RESET} The optimizer may struggle with certain content types"
echo -e "2. ${BOLD}Try different modes:${RESET} Instead of 'auto', try explicitly using 'docs', 'code', etc."
echo -e "3. ${BOLD}Update optimization rules:${RESET} Check the patterns in optimization_rules.py"
echo -e "4. ${BOLD}Examine reports:${RESET} The optimization reports contain detailed information"
echo

print_info "Diagnostic complete"
