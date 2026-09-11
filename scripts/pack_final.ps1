Write-Host "Re-packaging because source code changed..."
Remove-Item -Recurse -Force dist\TRON-DeCypher-v1.0.0 -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path dist\TRON-DeCypher-v1.0.0 | Out-Null
New-Item -ItemType Directory -Force -Path dist\TRON-DeCypher-v1.0.0\cases | Out-Null
New-Item -ItemType Directory -Force -Path dist\TRON-DeCypher-v1.0.0\logs | Out-Null
New-Item -ItemType Directory -Force -Path dist\TRON-DeCypher-v1.0.0\tools | Out-Null
Copy-Item -Recurse -Force -Path dist\TRON-DeCypher\* -Destination dist\TRON-DeCypher-v1.0.0\ -ErrorAction SilentlyContinue
Copy-Item -Path .env.example -Destination dist\TRON-DeCypher-v1.0.0\.env -ErrorAction SilentlyContinue
New-Item -ItemType File -Force -Path dist\TRON-DeCypher-v1.0.0\.portable | Out-Null
Compress-Archive -Path dist\TRON-DeCypher-v1.0.0\* -DestinationPath dist\TRON-DeCypher-v1.0.0-windows-x64.zip -Force
Write-Host "Build Complete! Located in: dist\TRON-DeCypher-v1.0.0-windows-x64.zip"
