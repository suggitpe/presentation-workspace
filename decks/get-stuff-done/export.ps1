param(
    [string]$Theme = "black",
    [string]$Output = "get-stuff-done.pdf",
    [int]$Port = 8008
)

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (!(Test-Path $chrome)) {
    $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}

Write-Host "Starting preview server on port $Port..."
$proc = Start-Process python -ArgumentList "-m", "http.server", "$Port", "--directory", "$PSScriptRoot" -PassThru
Start-Sleep -Seconds 2

try {
    $url = "http://localhost:$Port/?theme=$Theme&print-pdf"
    Write-Host "Exporting PDF with theme '$Theme' to $Output..."
    Start-Process $chrome -ArgumentList "--headless", "--disable-gpu", "--print-to-pdf=$PSScriptRoot\$Output", "--print-to-pdf-no-header", "--enable-background-graphics", "--window-size=1920,1080", "$url" -Wait
    Write-Host "Done: $Output"
} finally {
    Stop-Process -Id $proc.Id -Force
}
