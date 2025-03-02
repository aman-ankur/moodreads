#!/usr/bin/env python3
"""
Simple test script to check if Python is working correctly.
"""

import os
import sys

def main():
    """Print basic system information."""
    print("Python Test Script")
    print("-----------------")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    print("Test completed successfully.")

if __name__ == "__main__":
    main() 