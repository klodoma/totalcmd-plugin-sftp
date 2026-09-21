# `claude/` — the Claude-only layer

*Authored in `agent-standards/claude/`; this same file ships as `<repo>/.claude/README.md`.*

A separate source folder from `shared/`, delivered the same way. `agents-sync` vendors
`claude/skills/` and `claude/commands/` into `<repo>/.claude/`, exactly as it vendors
`shared/` into `<repo>/.agents/`, and `MANIFEST.json` covers both.

**Separate source**, because `shared/` is read by Codex and Cursor too and nothing
Claude-only belongs there. **Same delivery**, because `.agents/commands.md` promises that
`MRR <n>` behaves the same in every repo, and a skill installed only at `~/.claude/skills/`
keeps that promise on exactly one machine. Vendored, it travels with the checkout, so v30,
CI and a fresh worktree all have it.

| Path | What |
|---|---|
| `skills/mr/` | The deep read-only review of a merge request by number. Was `~/.claude/skills/mr` |
| `commands/` | Thin `/` wrappers over `.agents/commands.md` |

## The commands carry no rules

Each wrapper says which token of `commands.md` it is and points at the shared file for the
behaviour. That is deliberate: a rule written in two places drifts, and then `AIF` typed as
a bare word and `/aif` mean two different things — which is the one thing a fixed vocabulary
exists to prevent. Change the behaviour in `shared/commands.md`; the wrapper only needs to
change if the token does.

This is also why the vocabulary degrades gracefully. `commands.md` defines each token's
*behaviour*, not its tooling, so an agent with nothing installed does the work by hand and
`MRR <n>` still means one thing.

## There is deliberately no `/merge`

`MERGE` is the only command that crosses a gate: typing it *is* the human go-ahead that
`workflow.md` requires. It is already barred from a command list for that reason, and it is
the one action that cannot be taken back. Ergonomics are not worth anything on the step
whose whole value is that it costs a deliberate message.

## Never edit the vendored copy

`<repo>/.claude/skills/` and `<repo>/.claude/commands/` are written by `agents-sync`. Edit
one and the next sync overwrites it, while `agents-sync check` fails in the meantime. Change
it here and sync.

A repo's *own* Claude files — `.claude/launch.json`, `settings.json`, a skill that only
makes sense in that repo — are untouched by the sync, which only ever writes the paths named
in the manifest.
