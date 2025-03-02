#!/bin/bash
# Script to run Python scripts with the virtual environment activated

# Get the absolute path of the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Activate the virtual environment
source "$PROJECT_ROOT/.moodreads-env/bin/activate"

# Print environment information
echo "=== Environment Information ==="
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Project root: $PROJECT_ROOT"
echo "============================="

# Run the specified script with arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <script_name> [arguments]"
    echo "Example: $0 check_database.py"
    exit 1
fi

SCRIPT="$1"
shift  # Remove the script name from the arguments

# Check if the script exists
if [ ! -f "$PROJECT_ROOT/scripts/$SCRIPT" ]; then
    echo "Error: Script '$SCRIPT' not found in $PROJECT_ROOT/scripts/"
    exit 1
fi

echo "Running: python $PROJECT_ROOT/scripts/$SCRIPT $@"
python "$PROJECT_ROOT/scripts/$SCRIPT" "$@"

# Deactivate the virtual environment
deactivate 