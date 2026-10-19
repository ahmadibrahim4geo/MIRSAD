param([Parameter(Mandatory=$true)][string]$CertificateThumbprint)
# Use only a certificate the developer explicitly provides for this candidate.
$ErrorActionPreference = 'Stop'
$desktopRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$exePath = Join-Path $desktopRoot 'runtime\development\MIRSAD.exe'
$certificate = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Thumbprint -eq $CertificateThumbprint }
if (-not $certificate -or -not $certificate.HasPrivateKey -or $certificate.NotAfter -lt (Get-Date)) { throw 'A valid code-signing certificate with its private key is required.' }
$result = Set-AuthenticodeSignature -LiteralPath $exePath -Certificate $certificate -HashAlgorithm SHA256 -TimestampServer 'http://timestamp.digicert.com'
if ($result.Status -ne 'Valid') { throw ('Signature verification failed: '+$result.StatusMessage) }
# Signing changes the binary; an approval for the unsigned hash is invalid.
& (Join-Path $desktopRoot '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'refresh_candidate.py')
if ($LASTEXITCODE -ne 0) { throw 'Signed candidate revalidation failed; do not promote.' }
Write-Output 'Signature valid and candidate revalidated. Review the new bundle hash before promotion.'
