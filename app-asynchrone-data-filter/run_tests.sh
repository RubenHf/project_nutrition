#!/bin/bash

set -e  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest test_main.py