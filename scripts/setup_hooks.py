#!/usr/bin/env python3
"""
Setup script for Git hooks.

This script sets up Git hooks to run validation scripts before commits.
"""

import os
import sys
import stat
from pathlib import Path

def main():
    """Set up Git hooks."""
    try:
        print("Setting up Git hooks...")
        
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Create the hooks directory if it doesn't exist
        hooks_dir = project_root / ".git" / "hooks"
        if not hooks_dir.exists():
            print(f"Creating hooks directory: {hooks_dir}")
            hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the pre-commit hook
        pre_commit_path = hooks_dir / "pre-commit"
        
        pre_commit_content = """#!/bin/bash
# Pre-commit hook to run validation scripts

echo "Running interface validation..."
python scripts/validate_interfaces.py

# Check the exit code
if [ $? -ne 0 ]; then
    echo "Interface validation failed. Please fix the errors before committing."
    exit 1
fi

echo "Running unit tests..."
python -m unittest discover tests

# Check the exit code
if [ $? -ne 0 ]; then
    echo "Unit tests failed. Please fix the errors before committing."
    exit 1
fi

echo "All checks passed!"
exit 0
"""
        
        # Write the pre-commit hook
        with open(pre_commit_path, 'w') as f:
            f.write(pre_commit_content)
        
        # Make the pre-commit hook executable
        os.chmod(pre_commit_path, os.stat(pre_commit_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"Created pre-commit hook: {pre_commit_path}")
        print("Git hooks setup complete!")
        
    except Exception as e:
        print(f"Error setting up Git hooks: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 