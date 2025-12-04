#!/bin/bash
# Test runner script that sets TESTING environment variable

# Set the testing flag
export TESTING=true

# Run pytest with all arguments passed to this script
.venv/bin/python3 -m pytest "$@"
