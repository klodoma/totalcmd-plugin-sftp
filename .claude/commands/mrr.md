---
description: Deep read-only review of a GitLab merge request by number or URL
argument-hint: "<mr number or URL>"
---

Run `~MRR $ARGUMENTS` as `.agents/commands.md` defines it: use the `mr` skill in
`.claude/skills/mr/` and follow it exactly.

Read-only. Never post a comment, approve, merge or check the branch out, however good the
change is -- the verdict goes in chat and the owner decides what reaches GitLab.

A bare number always means this repo's merge request. Another project's has to arrive as a
full URL or `group/repo!<n>`.
