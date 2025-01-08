#!/bin/bash

# Set environment variables
export CLIENT_ID="Cp1pp6zBiWRHHRIUx7QKMw"
export CLIENT_SECRET="l4USlurNJUOGGvojzSPTCE1ws404Jw"
export USER_AGENT="RedditScript/0.1 by YourRedditUsername"

# Define the path to the Python executable and the script
PYTHON_PATH="./venv/Scripts/python"  # For Windows, use venv\Scripts\python
SCRIPT_PATH="C:/Users/Denis/Projects/Maksym_Afanasiev_Reddit_task/main.py"  # Absolute path to your Python script

# Check if the Python executable exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Python executable not found at $PYTHON_PATH"
    exit 1
fi

# Check if the Python script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found at $SCRIPT_PATH"
    exit 1
fi

# Run the Python script
echo "Running the Python script..."
"$PYTHON_PATH" "$SCRIPT_PATH"

# Output message after the script has finished running
echo "Script ran successfully"
