$env:CLIENT_ID="Cp1pp6zBiWRHHRIUx7QKMw"
$env:CLIENT_SECRET="l4USlurNJUOGGvojzSPTCE1ws404Jw"
$USER_AGENT="RedditScript/0.1 by YourRedditUsername"

$pythonPath = ".\venv\Scripts\python.exe"
$scriptPath = "C:\Users\Denis\Projects\Maksym_Afanasiev_Reddit_task\main.py"

& $pythonPath $scriptPath

Write-Host "Script ran"