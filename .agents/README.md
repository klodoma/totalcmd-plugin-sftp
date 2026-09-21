# `.agents/` — vendored shared rules

These files are **copied in from the `agent-standards` repo. Do not edit them here** — the
next sync overwrites the change and the drift check fails in the meantime.

To change a rule: open a merge request on `agent-standards`. Once it merges,
`agents-sync.py pull` brings it into each repo as its own MR. `agents-sync.py check` is
read-only and exits 1 if anything here has been edited locally, so it can run in CI or a
pre-commit hook.

`MANIFEST.json` records the upstream commit and date these files came from, so "how old are
these instructions" is answerable with `cat` — which matters on server checkouts, where the
tree can be far behind `main`.

| File | Covers |
|---|---|
| `workflow.md` | branches, the MR lifecycle, the merge gate, `glab`, where findings go |
| `communication.md` | how to report, the status line, verification discipline |
| `commands.md` | the short command vocabulary — `BPMR`, `AIF`, `MERGE` … |
| `review.md` | working a round with the GitLab AI reviewer |
| `secrets.md` | what never gets printed, what must not be regenerated |
| `infra.md` | the servers, folder layout, ports, the devauth gate |

`.claude/skills/` and `.claude/commands/` are vendored by the same tool, from
`agent-standards/claude/`, and the same rule applies to them — see `.claude/README.md`. The
repo's *own* Claude files (`launch.json`, `settings.json`) are never touched: the sync writes
only the paths named in `MANIFEST.json`.

The repo's own `AGENTS.md` takes precedence over all of them.
