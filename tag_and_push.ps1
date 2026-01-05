# Script to create a new git tag by incrementing the current tag and push it
# Assumes git add and git commit have already been done
# Usage: .\tag_and_push.ps1 [-Major|-Minor|-Patch]
# Default: -Patch

param(
    [switch]$Major,
    [switch]$Minor,
    [switch]$Patch
)

$ErrorActionPreference = "Stop"

# Determine which version component to increment
$incrementType = "patch"
if ($Major) {
    $incrementType = "major"
} elseif ($Minor) {
    $incrementType = "minor"
} elseif ($Patch) {
    $incrementType = "patch"
}

# Get the latest tag
$latestTag = git describe --tags --abbrev=0 2>$null

if ([string]::IsNullOrEmpty($latestTag)) {
    # No tags exist, start with v1.0.0
    $newTag = "v1.0.0"
    Write-Host "No existing tags found. Creating initial tag: $newTag" -ForegroundColor Green
} else {
    # Remove 'v' prefix if present for processing
    $version = $latestTag -replace '^v', ''
    
    # Split version into major.minor.patch
    $versionParts = $version -split '\.'
    $major = if ($versionParts[0]) { [int]$versionParts[0] } else { 0 }
    $minor = if ($versionParts[1]) { [int]$versionParts[1] } else { 0 }
    $patch = if ($versionParts[2]) { [int]$versionParts[2] } else { 0 }
    
    # Increment based on type (following semver rules)
    switch ($incrementType) {
        "major" {
            $major++
            $minor = 0
            $patch = 0
        }
        "minor" {
            $minor++
            $patch = 0
        }
        "patch" {
            $patch++
        }
    }
    
    # Reconstruct version with 'v' prefix
    $newTag = "v${major}.${minor}.${patch}"
    Write-Host "Latest tag: $latestTag" -ForegroundColor Cyan
    Write-Host "Incrementing: $incrementType" -ForegroundColor Yellow
    Write-Host "Creating new tag: $newTag" -ForegroundColor Green
}

# Create the tag
git tag $newTag

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create tag" -ForegroundColor Red
    exit 1
}

# Push the tag to remote
Write-Host "Pushing tag $newTag to remote..." -ForegroundColor Yellow
git push origin $newTag

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push tag" -ForegroundColor Red
    exit 1
}

Write-Host "Successfully created and pushed tag: $newTag" -ForegroundColor Green

