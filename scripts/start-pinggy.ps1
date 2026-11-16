$ErrorActionPreference = 'Stop'
Write-Host 'Giữ cửa sổ này mở. Chép URL HTTPS được cấp vào OLLAMA_BASE_URL trong .env.'
ssh -o ServerAliveInterval=30 -p 443 -R0:127.0.0.1:11434 free.pinggy.io
