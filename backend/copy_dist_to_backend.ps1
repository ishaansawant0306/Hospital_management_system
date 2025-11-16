# Copy built frontend (dist) into backend Templates/ and Static/
# Usage: Run from backend folder or CMD: powershell -ExecutionPolicy Bypass -File copy_dist_to_backend.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent $scriptDir
$dist = Join-Path $repoRoot 'frontend-clean\dist'
$backendTemplates = Join-Path $scriptDir 'Templates'
$backendStatic = Join-Path $scriptDir 'Static'

Write-Host "Script directory: $scriptDir" -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot" -ForegroundColor Cyan
Write-Host "Dist path: $dist" -ForegroundColor Cyan
Write-Host "Backend Templates: $backendTemplates" -ForegroundColor Cyan
Write-Host "Backend Static: $backendStatic" -ForegroundColor Cyan

if (-not (Test-Path $dist)) {
    Write-Host "ERROR: dist folder not found at $dist" -ForegroundColor Red
    Write-Host "Please run 'npm run build' in frontend-clean first." -ForegroundColor Red
    exit 1
}

# Ensure backend folders exist
if (-not (Test-Path $backendTemplates)) {
    New-Item -ItemType Directory -Path $backendTemplates -Force | Out-Null
    Write-Host "Created Templates folder: $backendTemplates" -ForegroundColor Green
}

if (-not (Test-Path $backendStatic)) {
    New-Item -ItemType Directory -Path $backendStatic -Force | Out-Null
    Write-Host "Created Static folder: $backendStatic" -ForegroundColor Green
}

# Copy index.html
$srcIndex = Join-Path $dist 'index.html'
$dstIndex = Join-Path $backendTemplates 'index.html'
if (Test-Path $srcIndex) {
    Copy-Item -Path $srcIndex -Destination $dstIndex -Force
    Write-Host "Copied index.html to Templates/" -ForegroundColor Green
} else {
    Write-Host "WARNING: index.html not found in dist" -ForegroundColor Yellow
}

# Copy static subdirectories: css, js, img, fonts, assets
$staticDirs = @('css', 'js', 'img', 'fonts', 'assets')
foreach ($dir in $staticDirs) {
    $src = Join-Path $dist $dir
    $dst = Join-Path $backendStatic $dir
    if (Test-Path $src) {
        # Remove existing folder if present to ensure clean copy
        if (Test-Path $dst) {
            Remove-Item -Path $dst -Recurse -Force
        }
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        Write-Host "Copied $dir/ to Static/" -ForegroundColor Green
    }
}

# Copy favicon.ico if present
$srcFavicon = Join-Path $dist 'favicon.ico'
$dstFavicon = Join-Path $backendStatic 'favicon.ico'
if (Test-Path $srcFavicon) {
    Copy-Item -Path $srcFavicon -Destination $dstFavicon -Force
    Write-Host "Copied favicon.ico to Static/" -ForegroundColor Green
}

Write-Host "Build artifacts copied successfully!" -ForegroundColor Green
Write-Host "You can now run Flask with: python main.py" -ForegroundColor Cyan
