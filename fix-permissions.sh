#!/bin/bash
# Fix permissions for Content Optimizer scripts

echo "Fixing permissions for Content Optimizer scripts..."

# Make optimize-quick.sh executable
chmod +x optimize-quick.sh
echo "✓ Made optimize-quick.sh executable"

# Make optimize.py executable
chmod +x optimize.py
echo "✓ Made optimize.py executable"

# Make this script executable (in case it wasn't)
chmod +x fix-permissions.sh
echo "✓ Made fix-permissions.sh executable"

echo "Done! You can now run ./optimize-quick.sh"
