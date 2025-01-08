$pythonPath = ".\venv\Scripts\python.exe"
$scriptPath = "absolute_path_to_main.py\main.py"
$inputUrlPath = Read-Host "Enter the input URL path"
$outputFilePath = Read-Host "Enter the output file path"
& $pythonPath $scriptPath $inputUrlPath $outputFilePath

Write-Host "Script ran"