Write-Host "Packaging Portable Release..."
$ReleaseDir = "dist\TRON-DeCypher-v1.0.0"
if (Test-Path $ReleaseDir) { Remove-Item -Recurse -Force $ReleaseDir }
New-Item -ItemType Directory -Path $ReleaseDir

Move-Item -Path "dist\TRON-DeCypher\*" -Destination $ReleaseDir

New-Item -ItemType Directory -Path "$ReleaseDir\cases"
New-Item -ItemType Directory -Path "$ReleaseDir\logs"
New-Item -ItemType Directory -Path "$ReleaseDir\tools"

New-Item -ItemType File -Path "$ReleaseDir\.portable"
Copy-Item -Path "README.md" -Destination "$ReleaseDir\README.txt"

Write-Host "Calculating SHA256..."
$hash = Get-FileHash -Path "$ReleaseDir\TRON-DeCypher.exe" -Algorithm SHA256
$hash.Hash | Out-File "$ReleaseDir\checksum.txt"

Write-Host "Build Complete! Located in: $ReleaseDir"
