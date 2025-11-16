# Copy built frontend (dist) into backend Templates/ and Static/
# Usage: run from repo root after `cd frontend-clean; npm run build` completes

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$dist = Join-Path $repoRoot 'frontend-clean\dist'
$backendTemplates = Join-Path $repoRoot 'backend\Templates'
$backendStatic = Join-Path $repoRoot 'backend\Static'

if (-not (Test-Path $dist)) {
    Write-Error "dist folder not found at $dist. Run 'npm run build' in frontend-clean first."
    exit 1
}

# Ensure backend folders exist
if (-not (Test-Path $backendTemplates)) { New-Item -ItemType Directory -Path $backendTemplates | Out-Null }
if (-not (Test-Path $backendStatic)) { New-Item -ItemType Directory -Path $backendStatic | Out-Null }

# Copy index.html
Copy-Item -Path (Join-Path $dist 'index.html') -Destination (Join-Path $backendTemplates 'index.html') -Force

# Copy common static folders (css, js, img, fonts) and favicon
$staticNames = @('css','js','img','fonts','fonts','assets')
foreach ($name in $staticNames) {
    $src = Join-Path $dist $name
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination (Join-Path $backendStatic $name) -Recurse -Force
    }
}

# Copy favicon if present
$favicon = Join-Path $dist 'favicon.ico'
if (Test-Path $favicon) {
    Copy-Item -Path $favicon -Destination (Join-Path $backendStatic 'favicon.ico') -Force
}

Write-Host "Copied dist to backend/Templates and backend/Static successfully." -ForegroundColor Green
