#!/bin/bash

pythonPath="./venv/bin/python"
scriptPath="absolute_path_to_main.py/main.py"

# Prompt for user input
read -p "Enter the input URL path: " inputUrlPath
read -p "Enter the output file path: " outputFilePath

# Run the Python script
$pythonPath $scriptPath "$inputUrlPath" "$outputFilePath"

echo "Script ran"
