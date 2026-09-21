---
description: Branch, commit and push what is in the tree, then open the merge request
argument-hint: "<branch slug>"
---

Run `~BPMR $ARGUMENTS` as `.agents/commands.md` defines it, following the lifecycle in
`.agents/workflow.md`.

- Branch off `main` with the prefix this repo already uses -- check `git branch -r` rather
  than inventing one.
- **Commit only this task's changes.** Other agents may be working in the same tree; do not
  sweep up files you did not touch.
- The commit message is long and explains the reasoning. Read recent commits first.
- If the branch already has an open merge request, push and update that description instead
  of opening a second one.

Stop there. Opening the merge request is the end of this command -- `.agents/workflow.md`
puts the merge behind an explicit human go-ahead, and nothing here is one.
