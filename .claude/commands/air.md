---
description: Ask the GitLab AI reviewer for a round on this branch's merge request
argument-hint: "[mr number]"
---

Run `~AIR $ARGUMENTS` as `.agents/commands.md` defines it, following the loop in
`.agents/review.md`.

Read both of those files before acting; this command carries no rules of its own, so that
`AIR` typed as a bare word and `/air` can never mean two different things.

The two points that are easy to get wrong:

- **Which request to send.** First round, when `ai-reviewer` is not yet a reviewer:
  `glab mr update <n> --reviewer +ai-reviewer`. Every later round: `glab mr note create <n>
  -m "/review" --resolvable=false`. Re-adding a reviewer who is already assigned triggers
  nothing at all.
- **The open-thread guard applies every round.** If any thread is still open, refuse, name
  them, and stop. Do not send `/review` to look busy.

Then wait for the placeholder note to become the result, read the threads **and** the
summary note, and list every finding. Do not fix anything here -- that is `~AIF`.
