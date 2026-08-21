#!/usr/bin/env pwsh
<#
.SYNOPSIS
	Builds sftpplug.zip from the artifacts\ directory (static files) plus the
	compiled wfx\sftpplug.wfx (32-bit) and wfx\sftpplug.wfx64 (64-bit).
	Output: dist\sftpplug.zip
.PARAMETER Version
	Optional version string. When provided the zip is named sftpplug-<Version>.zip.
#>
param(
	[string]$Version = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PackDir     = Join-Path $ProjectRoot "artifacts"
$WfxDir      = Join-Path $ProjectRoot "wfx"
$OutputDir   = Join-Path $ProjectRoot "dist"
$ZipName     = if ($Version) { "sftpplug-$Version.zip" } else { "sftpplug.zip" }
$OutputZip   = Join-Path $OutputDir $ZipName

$Wfx32 = Join-Path $WfxDir "sftpplug.wfx"
$Wfx64 = Join-Path $WfxDir "sftpplug.wfx64"

foreach ($f in @($Wfx32, $Wfx64)) {
	if (-not (Test-Path $f)) {
		Write-Error "Required build output not found: $f"
		exit 1
	}
}

if (-not (Test-Path $OutputDir)) {
	New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Always build fresh
if (Test-Path $OutputZip) {
	Remove-Item $OutputZip -Force
}

Write-Host ""
Write-Host "=== Packaging sftpplug.zip ===" -ForegroundColor Cyan

$zip = [System.IO.Compression.ZipFile]::Open($OutputZip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
	# Add all static files from artifacts\ preserving relative paths
	Get-ChildItem -Recurse -File $PackDir | ForEach-Object {
		$entryName = $_.FullName.Substring($PackDir.Length + 1).Replace("\", "/")
		[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
			$zip,
			$_.FullName,
			$entryName,
			[System.IO.Compression.CompressionLevel]::Optimal
		) | Out-Null
		Write-Host "  Added    : $entryName"
	}

	# Add compiled plugin files
	foreach ($entry in @(@{ Name = "sftpplug.wfx"; Path = $Wfx32 }, @{ Name = "sftpplug.wfx64"; Path = $Wfx64 })) {
		[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
			$zip,
			$entry.Path,
			$entry.Name,
			[System.IO.Compression.CompressionLevel]::Optimal
		) | Out-Null
		Write-Host "  Added    : $($entry.Name)"
	}
} finally {
	$zip.Dispose()
}

Write-Host ""
Write-Host "=== Package complete ===" -ForegroundColor Green
Write-Host "  $OutputZip"
Write-Host ""

# Show final zip contents
$reader = [System.IO.Compression.ZipFile]::OpenRead($OutputZip)
try {
	$reader.Entries | ForEach-Object {
		Write-Host ("  {0,-30} {1,8} bytes" -f $_.FullName, $_.Length)
	}
} finally {
	$reader.Dispose()
}
