#!/bin/bash

# Script to fix permissions for executable files in the Content Optimizer
echo "Fixing permissions for executable scripts..."

# Make the main optimize script executable
if [ -f "./optimize.py" ]; then
  chmod +x ./optimize.py
  echo "✓ Made optimize.py executable"
else
  echo "⚠ Warning: optimize.py not found"
fi

# Make the optimize-quick script executable
if [ -f "./optimize-quick.sh" ]; then
  chmod +x ./optimize-quick.sh
  echo "✓ Made optimize-quick.sh executable"
else
  echo "⚠ Warning: optimize-quick.sh not found"
fi

# Make the new training data generator executable
if [ -f "./generate_training_data.py" ]; then
  chmod +x ./generate_training_data.py
  echo "✓ Made generate_training_data.py executable"
else
  echo "⚠ Warning: generate_training_data.py not found"
fi

# Make this script executable (for future runs)
chmod +x "$0"
echo "✓ Made fix-permissions.sh executable"

echo "Done!"
