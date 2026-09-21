---
description: Print the status line for the current merge request, and nothing else
argument-hint: "[mr number]"
---

Run `~ST $ARGUMENTS` as `.agents/commands.md` defines it, in the form
`.agents/communication.md` specifies.

One line, nothing before it and nothing after it:

    READY: !88 @ 4b0a4d7 · https://gitlab.evo21.ch/interpid/auto-trader/-/merge_requests/88

`READY` / `NOT READY` / `NEEDS FEEDBACK` / `MERGED`, the exact head commit, and the full URL
bare rather than as a markdown link. `NOT READY` and `NEEDS FEEDBACK` need a clause saying
what is missing. Never `READY` with a known finding outstanding, or before pushing.
