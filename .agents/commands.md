# Short commands

A fixed vocabulary for the actions asked for most often, so that three keystrokes get the
same behaviour every time, in every repo.

**A message is either entirely commands, or it is prose.** Split it on commas and line
breaks; every part must parse as one command with exactly the arguments that command takes.
One part that does not parse makes the whole message prose — then ask, and run none of it.

```text
MR                        one command
B docs/rename, P, MR      three, run in that order
AIR 1                     one, with its argument
MR 48 has conflicts       prose: MR takes no argument, so "48 has conflicts" is left over
AIF, and check CI after   prose: the second part is not a command
I wouldn't ~P that yet    prose: one part, and it does not parse
```

That is the whole rule, and it needs nothing about *where* in a message a command may sit: a
message carrying anything else is not a command message at all. Which is what stops a negated
or quoted token — "do not `~MERGE` yet", or this very file quoted back at you — from ever
firing.

**Both spellings work and mean the same thing: `~AIF` and `AIF` are one command**, for every
command in the tables below, and they may be mixed in one list. The tilde is stylistic: the
parse is what makes a command unambiguous, so `~` adds nothing the rule above does not already
give. It stays until there is enough use to show which spelling people actually type. It is
`~` rather than something more obvious because every more obvious character is taken in the
terminal these are typed into — `/` by slash commands, `#` by add-to-memory, `@` by file
completion, `:` by emoji, `!` by running a shell command.

**`MERGE` is the one exception: it must be alone**, never a part in a list. Everything else
can ride in a batch, but a batch is fired without necessarily re-reading its tail, and this is
the one action that cannot be taken back. Typing it *is* the human go-ahead `workflow.md`
requires, so it costs a message of its own.

Nothing completes these: they work because an agent read this file. A token that is not on
this list is not a command — ask rather than guess, since all of them touch git or GitLab.

**A merge request number always means this repo's.** One session works on one project, so
`~MRR 56` and `MRR 56` both mean a merge request in the repo the session is rooted in. Never
resolve a bare number against another project, and if a command arrives while no repo is in
scope, ask which one rather than picking. A number for a different project has to be given as
a full URL or `group/repo!56`, and that is the only time the session crosses over. Where the
tables write `[<n>]` the number is optional, and leaving it out means the merge request for
the current branch.

## Making the change

| Type | Means |
|---|---|
| `~B <slug>` | Branch off `main`, using the prefix the repo already uses. Never commit on `main` |
| `~P` | Commit what is in the tree and push. Only this task's changes — other agents may be working in the same tree |
| `~BP <slug>` | `~B` then `~P` |
| `~MR` | Open the merge request for the current branch. If one is already open, push and update its description instead — one MR per branch |
| `~BPMR <slug>` | `~B` + `~P` + `~MR`. The whole thing, when the work is already sitting in the tree |

## Review

| Type | Means |
|---|---|
| `~AIR [<n>]` | Ask the GitLab AI reviewer. First round: add `ai-reviewer` as Reviewer. Every later round: confirm no thread is still open — if any are, refuse and name them — then comment `/review`. Wait for the result, then list the findings |
| `~AIF [<n>]` | Act on the AI reviewer's feedback, end to end: read every open thread **and** the summary-only findings, fix or argue each one, reply in the thread it came from, push, resolve the threads that push fixed, and say what is left |
| `~MRR <n>` | A deep read-only review of MR `<n>` — the `mr` skill. Never posts, approves or merges |
| `~APPROVE <n>` | Approve MR `<n>`. Someone else's only, never your own branch |

## Finishing

| Type | Means |
|---|---|
| `~ST [<n>]` | Print the status line for the current MR (see `communication.md`), and nothing else |
| `~SC` | Save context: write or update `session-context/<branch>.md` and commit it, in repos that have the folder |
| `~MERGE [<n>]` | Merge the MR. **Typing this, alone in its own message, is the human go-ahead** that `workflow.md` requires — nothing else counts as one |

## Notes

- `~MERGE` is the only command that crosses a gate, and so the only one barred from a list
  (above). Everything else is additive or reversible, so run them without asking.
- **There is no separate re-review command.** Steps 1 and 6 of `review.md` are the same
  request split by round, so `~AIR` is both, and the open-thread guard applies every time.
- `~AIF` ends where the work ends, not where the round ends: if findings remain unanswered,
  say so rather than firing `~AIR` again to look finished.
- `/review` keeps its slash: it is not one of these commands but a comment posted **to GitLab**,
  where the reviewer bot reads it. `~AIR` is what posts it.
- `/code-review`, `/simplify` and `/security-review` are Claude Code built-ins that read the
  *local* tree and do not talk to GitLab. `~MRR <n>` is the GitLab one.
- On the GitHub repos (`totalcmd-plugin-sftp`), `~MR` means pull request and the tool is `gh`.
  There is no AI reviewer there, so `~AIR` and `~AIF` do not apply.
