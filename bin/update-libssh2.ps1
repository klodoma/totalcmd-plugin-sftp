#!/usr/bin/env pwsh
<#
.SYNOPSIS
	Refreshes the bundled libssh2.dll (32-bit) and 64\libssh2.dll (64-bit) in
	deps\libssh2\ from the official upstream plugin package by Ghisler Software.
	These builds use the Windows CNG crypto backend (no OpenSSL dependency) and
	carry upstream's security backports.

	After running, review and commit deps\libssh2\ including libssh2.sha256.
.PARAMETER Url
	Upstream plugin zip to take the DLLs from.
#>
param(
	[string]$Url = "https://www.totalcommander.ch/win/fs/sftpplug.zip"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DepsDir     = Join-Path $ProjectRoot "deps\libssh2"
$TempDir     = Join-Path ([System.IO.Path]::GetTempPath()) ("libssh2-" + [guid]::NewGuid())
$TempZip     = Join-Path $TempDir "sftpplug.zip"

New-Item -ItemType Directory -Path $TempDir | Out-Null
try {
	Write-Host "Downloading $Url" -ForegroundColor Cyan
	Invoke-WebRequest -Uri $Url -OutFile $TempZip -UseBasicParsing

	$ExtractDir = Join-Path $TempDir "x"
	[System.IO.Compression.ZipFile]::ExtractToDirectory($TempZip, $ExtractDir)

	foreach ($rel in @("libssh2.dll", "64\libssh2.dll")) {
		$src = Join-Path $ExtractDir $rel
		if (-not (Test-Path $src)) {
			Write-Error "Upstream package does not contain $rel"
			exit 1
		}
		$dst = Join-Path $DepsDir $rel
		New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
		Copy-Item $src $dst -Force
		Write-Host ("  {0,-16} {1}" -f $rel, (Get-Item $dst).VersionInfo.FileVersion)
	}
} finally {
	Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
}

# Record hashes so pack.ps1 can verify it ships exactly these files.
$lines = foreach ($rel in @("libssh2.dll", "64/libssh2.dll")) {
	$hash = (Get-FileHash (Join-Path $DepsDir $rel) -Algorithm SHA256).Hash.ToLowerInvariant()
	"$hash  $rel"
}
Set-Content -Path (Join-Path $DepsDir "libssh2.sha256") -Value $lines -Encoding ascii

Write-Host ""
Write-Host "=== libssh2 updated ===" -ForegroundColor Green
$lines | ForEach-Object { Write-Host "  $_" }
