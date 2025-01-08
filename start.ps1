$pythonPath = ".\venv\Scripts\python.exe"
$scriptPath = "C:\Users\Denis\Projects\Maksym_Afanasiev_Reddit_task\main.py"
$inputUrlPath = Read-Host "Enter the input URL path"
$outputFilePath = Read-Host "Enter the output file path"
& $pythonPath $scriptPath $inputUrlPath $outputFilePath

Write-Host "Script ran"