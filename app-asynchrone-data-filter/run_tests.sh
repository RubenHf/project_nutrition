#!/bin/bash

echo "Script run_tests.sh..."
set -e  # Exit on error

# Run tests
echo "Running tests..."
pytest test_main.py