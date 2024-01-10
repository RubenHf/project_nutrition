#!/bin/bash

echo "Script run_tests.sh..."
set -e  # Exit on error

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest test_main.py