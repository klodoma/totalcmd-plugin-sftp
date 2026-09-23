#!/usr/bin/env pwsh
<#
.SYNOPSIS
	Builds sftpplug.zip from the artifacts\ directory (static files), the
	compiled wfx\sftpplug.wfx (32-bit) and wfx\sftpplug.wfx64 (64-bit), and the
	bundled libssh2.dll / 64\libssh2.dll from deps\libssh2\.
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

# Bundled libssh2 (see bin\update-libssh2.ps1). Without it the plugin falls back
# to whatever libssh2.dll is on PATH, which may be too old for modern servers.
$Libssh2Dir  = Join-Path $ProjectRoot "deps\libssh2"
$Libssh2Hash = Join-Path $Libssh2Dir "libssh2.sha256"
$Libssh2Files = @(
	@{ Name = "libssh2.dll";    Path = Join-Path $Libssh2Dir "libssh2.dll" },
	@{ Name = "64/libssh2.dll"; Path = Join-Path $Libssh2Dir "64\libssh2.dll" },
	@{ Name = "libssh2-COPYING.txt"; Path = Join-Path $Libssh2Dir "COPYING" }
)

foreach ($f in $Libssh2Files + @(@{ Path = $Libssh2Hash })) {
	if (-not (Test-Path $f.Path)) {
		Write-Error "Required libssh2 file not found: $($f.Path). Run bin\update-libssh2.ps1."
		exit 1
	}
}

foreach ($line in Get-Content $Libssh2Hash) {
	if (-not $line.Trim()) { continue }
	$expected, $rel = $line -split '\s+', 2
	$actual = (Get-FileHash (Join-Path $Libssh2Dir $rel) -Algorithm SHA256).Hash
	if ($actual -ne $expected) {
		Write-Error "SHA256 mismatch for deps\libssh2\$rel (expected $expected, got $actual)."
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

# Strip a leading "v" so pluginst.inf gets a numeric version (e.g. v3.20.2 -> 3.20.2)
$InfVersion = if ($Version) { $Version -replace '^[vV]', '' } else { "" }

$zip = [System.IO.Compression.ZipFile]::Open($OutputZip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
	# Add all static files from artifacts\ preserving relative paths
	Get-ChildItem -Recurse -File $PackDir | ForEach-Object {
		$entryName = $_.FullName.Substring($PackDir.Length + 1).Replace("\", "/")

		if ($InfVersion -and $_.Name -ieq "pluginst.inf") {
			# Rewrite the version line in-memory instead of touching the working tree
			$content = [System.IO.File]::ReadAllText($_.FullName)
			$newContent = [regex]::Replace(
				$content,
				'(?m)^\s*version\s*=.*$',
				"version=$InfVersion"
			)
			$entry = $zip.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
			$writer = New-Object System.IO.StreamWriter($entry.Open(), [System.Text.Encoding]::UTF8)
			try { $writer.Write($newContent) } finally { $writer.Dispose() }
			Write-Host "  Added    : $entryName (version=$InfVersion)"
		}
		else {
			[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
				$zip,
				$_.FullName,
				$entryName,
				[System.IO.Compression.CompressionLevel]::Optimal
			) | Out-Null
			Write-Host "  Added    : $entryName"
		}
	}

	# Add compiled plugin files and the bundled libssh2
	foreach ($entry in @(@{ Name = "sftpplug.wfx"; Path = $Wfx32 }, @{ Name = "sftpplug.wfx64"; Path = $Wfx64 }) + $Libssh2Files) {
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
