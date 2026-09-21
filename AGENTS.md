# AGENTS.md — totalcmd-plugin-sftp

A file-system plugin for Total Commander that browses a remote server over SFTP (file
transfer tunnelled through SSH). C/C++, built with MSBuild for both 32-bit and 64-bit
Windows, and shipped as a `.wfx` / `.wfx64` pair inside a ZIP the user installs from inside
Total Commander. The code is a maintained copy of Christian Ghisler's original plugin —
[README.md](README.md) has the provenance, and
[artifacts/readme.txt](artifacts/readme.txt) is the end-user documentation.

**Shared process rules live in `.agents/`** — `workflow.md` (branches, the review lifecycle,
the merge gate), `communication.md` (how to report, the status line), `commands.md` (the
short command vocabulary), `secrets.md`. Read them; they are not optional context. Where
this file disagrees with them, **this file wins** — and say so when you rely on that. Never
edit `.agents/` here: it is vendored from `agent-standards` (see `.agents/README.md`).

**This repo is the exception those files are written against.** §6 below says exactly what
is different, and it is the first thing to read, because `.agents/workflow.md` will
otherwise send you to the wrong tool and the wrong host.

---

## 1. GitHub, `gh`, and a pull request

The remote is `github.com/klodoma/totalcmd-plugin-sftp`. Not GitLab, not
`gitlab.evo21.ch`, and there is no `ai-reviewer` bot here.

Everywhere `.agents/` says `glab`, use `gh`; everywhere it says merge request, read pull
request; and the status line from `.agents/communication.md` uses `#9` and the pull-request
URL instead of `!9`. Nothing else about the lifecycle changes — branch, commit, push, open
the PR when the work is done, and **merge only after an explicit human go-ahead**.

    gh pr create --base main --head <branch> --title "<title>" --body-file /tmp/pr.md
    gh pr view <n>
    gh pr view <n> --comments
    gh pr merge <n>

## 2. Layout

| Path | What |
|---|---|
| `sftpplug.cpp`, `sftpfunc.cpp`, `multiserver.cpp`, `utils.cpp` | The plugin itself — the WFX entry points, the SFTP calls, the connection list |
| `fsplugin.h` | Total Commander's WFX plugin interface. **Ghisler's file — do not change it** |
| `sshdynload.h`, `sshdynfunctions.h`, `libssh2*.h` | libssh2, loaded dynamically at runtime |
| `cunicode.cpp`, `CVTUTF.C` | Character-set conversion, inherited from the original |
| `sftpplug.sln`, `sftpplug.vcxproj` | The MSBuild projects. The `.dsp`/`.dsw`/`.vcproj` files beside them are older Visual Studio formats, kept for reference |
| `bin/build.ps1`, `pack.ps1`, `release.ps1` | Build, package, and release. Use these rather than hand-running MSBuild |
| `artifacts/pluginst.inf`, `artifacts/readme.txt` | What ships inside the ZIP: the install descriptor and the user documentation |
| `.github/workflows/` | `ci.yml` builds both platforms on every push; `release.yml` runs on a `v*` tag |

## 3. Building

```powershell
bin/build.ps1                    # both platforms
bin/pack.ps1  -Version 1.2.3     # the installable ZIP
bin/release.ps1 -Version v1.2.3  # build + pack into dist/
```

CI builds `Release|Win32` **and** `Release|x64` and fails if either binary is missing. **A
change that compiles for one platform can fail on the other** — pointer width and the
`HANDLE`-sized fields in the WFX interface are where that happens — so build both before
pushing, or expect CI to tell you.

## 4. The version comes from the git tag

`release.ps1` takes `-Version`, and on a tag push `release.yml` passes `github.ref_name`.
`pack.ps1` strips a leading `v` and rewrites the `version=` line of `pluginst.inf`
**in memory** as it adds it to the ZIP, so the working tree is never touched and the ZIP
name, the shipped descriptor and the GitHub Release all carry the same number.

The tracked `artifacts/pluginst.inf` still holds a literal (`version=3.20.2`). It is the
fallback used only when packaging with no `-Version`, so **it is not the released version
and editing it does not change one.** Bump the tag, not that line.

Releasing is tagging: push a `v*` tag and the workflow builds, packages and publishes. That
is outward-facing and irreversible in the way `.agents/workflow.md` means, so it is the
owner's call, never an agent's.

## 5. Conventions and traps

- **Match the surrounding code.** It is old C/C++ in the original author's style, Windows
  API throughout, and consistency with the file beats modernising it. A tidy-up diff mixed
  into a fix is how a review stops being able to see the fix.
- **`fsplugin.h` is the contract with Total Commander.** Changing a signature there breaks
  the host silently rather than at compile time.
- **libssh2 is loaded dynamically** (`sshdynload.h`). A function used without being resolved
  first crashes at the call, not at load, and only on a machine without that library
  version.
- **Almost everything build-shaped is git-ignored** — `wfx/`, `Release/`, `x64/`, `dist/`,
  `*.wfx`, `*.wfx64`, `*.obj`. If a build output seems to be missing from the repo, that is
  why; do not commit around it.
- **ANSI and wide-character paths both exist** in the WFX interface. Check which one you are
  in before touching a string.

## 6. What this file overrides in `.agents/`

- **`workflow.md`** — GitHub and `gh` throughout, "pull request" for "merge request", and
  `#9` in the status line. The clone URL, port 5023, the protected-branch behaviour and the
  `glab` invocations are all GitLab facts and do not apply. The lifecycle and the merge gate
  do apply, unchanged.
- **`review.md`** — does not apply at all. There is no `ai-reviewer` bot on GitHub, so
  `~AIR` and `~AIF` have nothing to talk to. `~MRR` still works: the `mr` skill reads a
  merge request, and a GitHub pull request needs the reviewer to work from `gh` instead.
- **`infra.md`** — does not apply. This plugin runs on a user's Windows machine; there is no
  `evo21-v10`/`v30` in the picture, nothing is deployed, and no dev vhost exists.
- **`secrets.md` and `communication.md`** apply in full.
