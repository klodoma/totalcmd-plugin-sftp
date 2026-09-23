# Total Commander SFTP Plugin

A secure FTP plugin for Total Commander over SSH. It supports both 32-bit and
64-bit Windows installations.

## Source

This project is a copy of the original Total Commander SFTP plugin published
by Ghisler Software GmbH:

https://www.ghisler.com/plugins.htm

This copy is maintained at:

https://github.com/klodoma/totalcmd-plugin-sftp

The plugin is based on the Total Commander WFX plugin interface. Copyright for
the original plugin is held by Christian Ghisler.

## Installation

Copy the appropriate WFX file to the Total Commander plugin directory, or use
the ZIP package and install it through Total Commander's plugin installation.

The package ships its own `libssh2.dll` (32-bit) and `64\libssh2.dll` (64-bit).
Keep them next to the WFX files: without them the plugin falls back to any
`libssh2.dll` on `PATH` (e.g. one from PHP), which may be too old to log in to
current OpenSSH servers with RSA keys.

For supported features and configuration details, see
[artifacts/readme.txt](artifacts/readme.txt).
