#!/usr/bin/env pwsh
<#
.SYNOPSIS
	Installs the packaged plugin from dist\ into a Total Commander plugin folder
	by extracting the newest dist\sftpplug*.zip (or -Zip) over -Target.
	Close Total Commander first: loaded .wfx/.dll files cannot be overwritten.
.PARAMETER Target
	Plugin folder to install into.
.PARAMETER Zip
	Package to install. Defaults to the most recently written dist\sftpplug*.zip.
#>
param(
	[string]$Target = "C:\softkit\Totalcmd\plugins\sftpplug",
	[string]$Zip = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistDir     = Join-Path $ProjectRoot "dist"

if (-not $Zip) {
	$latest = Get-ChildItem -Path $DistDir -Filter "sftpplug*.zip" -File -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
	if (-not $latest) {
		Write-Error "No sftpplug*.zip found in $DistDir. Run bin\release.ps1 first."
		exit 1
	}
	$Zip = $latest.FullName
}
elseif (-not (Test-Path $Zip)) {
	Write-Error "Package not found: $Zip"
	exit 1
}

if (-not (Test-Path $Target)) {
	New-Item -ItemType Directory -Path $Target | Out-Null
}

Write-Host "=== Installing $(Split-Path -Leaf $Zip) ===" -ForegroundColor Cyan
Write-Host "  Target   : $Target"

$reader = [System.IO.Compression.ZipFile]::OpenRead($Zip)
try {
	foreach ($entry in $reader.Entries) {
		# Directory entries have an empty Name
		if (-not $entry.Name) { continue }

		$dest = Join-Path $Target ($entry.FullName.Replace("/", "\"))
		New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
		try {
			[System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $dest, $true)
		}
		catch [System.IO.IOException] {
			Write-Error "Cannot overwrite $dest - is Total Commander still running? Close it and retry."
			exit 1
		}
		Write-Host "  Copied   : $($entry.FullName)"
	}
} finally {
	$reader.Dispose()
}

Write-Host ""
Write-Host "=== Install complete ===" -ForegroundColor Green
