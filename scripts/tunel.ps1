param(
    [int]$Puerto = 8000
)

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared no está instalado. Instálalo con: winget install Cloudflare.cloudflared"
    exit 1
}

Write-Host "Abriendo túnel para http://127.0.0.1:$Puerto"
Write-Host "Presiona Ctrl+C para cerrar el túnel."

& cloudflared tunnel --url "http://127.0.0.1:$Puerto" 2>&1 | ForEach-Object {
    $linea = $_.ToString()
    Write-Host $linea
    if ($linea -match "https://[-a-zA-Z0-9]+\.trycloudflare\.com") {
        $direccion = $Matches[0]
        Write-Host ""
        Write-Host "================================================================"
        Write-Host "TÚNEL PÚBLICO: $direccion"
        Write-Host "Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES."
        Write-Host "================================================================"
        Write-Host ""
    }
}
