Write-Host "Building TRON-DeCypher v1.0.0..."
if (-not (Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" }

# Build using pyinstaller (directory mode is safer for complex assets than onefile)
.\venv\Scripts\pyinstaller --noconfirm --onedir --windowed --name "TRON-DeCypher" --add-data "config;config/" --add-data "docs;docs/" app/main.py

Write-Host "Packaging Portable Release..."
\ = "dist\TRON-DeCypher-v1.0.0"
if (Test-Path \) { Remove-Item -Recurse -Force \ }
New-Item -ItemType Directory -Path \

# Move compiled output to ReleaseDir
Move-Item -Path "dist\TRON-DeCypher\*" -Destination \

# Ensure directories exist for portable operation
New-Item -ItemType Directory -Path "\\cases"
New-Item -ItemType Directory -Path "\\logs"
New-Item -ItemType Directory -Path "\\tools"

# Create a portable marker so the app knows it's running portable
New-Item -ItemType File -Path "\\.portable"

# Copy README
Copy-Item -Path "README.md" -Destination "\\README.txt"

Write-Host "Calculating SHA256..."
\ = Get-FileHash -Path "\\TRON-DeCypher.exe" -Algorithm SHA256
\.Hash | Out-File "\\checksum.txt"

Write-Host "Build Complete! Located in: \"
