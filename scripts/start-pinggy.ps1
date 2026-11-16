$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$keyPath = Join-Path $root 'tmp\pinggy_key'
New-Item -ItemType Directory -Force -Path (Join-Path $root 'tmp') | Out-Null
if (-not (Test-Path -LiteralPath $keyPath)) {
    & (Join-Path $root '.venv\Scripts\python.exe') -c "import subprocess,sys; subprocess.run(['ssh-keygen','-q','-t','ed25519','-f',sys.argv[1],'-N',''],check=True)" $keyPath
    if ($LASTEXITCODE -ne 0) { throw 'Không tạo được khóa SSH riêng cho tunnel.' }
}
Write-Host 'Giữ cửa sổ này mở. Chép URL HTTPS được cấp vào OLLAMA_BASE_URL trong .env.'
ssh -t -i $keyPath -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -p 443 -R0:127.0.0.1:11434 free.pinggy.io 'u:Host:localhost:11434'
