---
description: Act on the GitLab AI reviewer's findings, end to end
argument-hint: "[mr number]"
---

Run `~AIF $ARGUMENTS` as `.agents/commands.md` defines it, following steps 3-5 of
`.agents/review.md`.

Read both files before acting. The three things the loop turns on:

- **Read both surfaces.** The threads and the summary note. A finding that could not be
  anchored to a line exists *only* in the summary, and reading threads alone loses it
  silently.
- **A reasoned refusal is a legitimate outcome, but it has to be written where the bot can
  read it** -- the merge request description, or `AGENTS.md` when it is a standing fact.
  The bot gets no notes or discussions as input, so a rebuttal posted only in the thread
  reaches the humans and not the next round, which will raise it again unchanged.
- **Resolve only after the fix is pushed**, and name the commit in the reply.

Finish with the status line from `.agents/communication.md`. If findings remain unanswered,
say so; `~AIF` ends where the work ends, not where the round ends.
