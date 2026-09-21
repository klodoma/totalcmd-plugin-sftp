---
name: mr
description: Code-review a GitLab merge request that is NOT checked out locally, given its number or URL — "/mr !88", "review MR 88", or a pasted .../-/merge_requests/N link. Fetches the MR's diff, description, commits, CI status and existing comments through glab, reads the changed code in its surrounding context, and reports prioritised P1/P2/P3 findings ending in a plain APPROVED or CHANGES REQUESTED verdict. Use it when the target is a merge request on gitlab.evo21.ch identified by number or link. For reviewing the branch or working tree that is already checked out, Claude Code's built-in code-review skill is the better fit. Read-only: it never posts, comments, approves or merges on GitLab.
---

# Review a GitLab merge request

A review earns its keep by finding what the author could not see themselves. Reciting the
diff back is worthless; so is approving because nothing jumped out. The goal is a small
number of findings you can defend, plus an honest verdict.

**This skill is read-only.** Fetch, read, reason, report in chat. Never post a comment,
approve, merge, push, or change the MR state — even when the review is glowing. The user
decides what reaches GitLab. Never check out the MR branch either; the working tree may hold
unrelated work in progress.

## Step 1 — Gather the context

```bash
python .claude/skills/mr/scripts/mr_context.py '!88' "$TMP/mr88"
```

The skill is vendored into each repo by `agents-sync`, so that path is inside the
checkout you are already in -- run it from the repo root. There is no copy under
`~/.claude/` to fall back on, deliberately: a skill installed on one machine cannot
keep `.agents/commands.md`'s promise that `MRR <n>` behaves the same everywhere.

Pass the target through as the user gave it — `!88`, `88`, or the full URL. Run it from the
repo the MR belongs to when you can, so the script can fetch the MR's commits locally.

It prints a header (state, author, branches, squash, conflicts, merge status, pipeline,
comment counts, base/head SHA) and writes a bundle: `mr.json`, `description.md`,
`diff.patch`, `files.txt`, `discussions.md`.

Read `diff.patch`, `description.md`, and `discussions.md` before forming any opinion.
`discussions.md` matters most — re-raising a point someone already made, or one the author
already answered, wastes everyone's time and makes the rest of the review easy to dismiss.

## Step 2 — Read the code, not only the diff

Diff hunks show changed lines with a few lines of padding. Most real bugs live in the
relationship between the change and the code around it: a caller that passes the argument
the new branch does not handle, an early `return` above the new block, a variable the hunk
reuses under a different meaning.

When the script reports `refs/mr/<N> fetched`:

```bash
git show refs/mr/88:scripts/envctl.sh          # whole file as the MR leaves it
git diff 37a296540b38..refs/mr/88              # GitLab's exact diff, reproduced
git log --oneline 37a296540b38..refs/mr/88     # the commits, in order
```

On Git Bash (Windows), a `ref:path` argument whose path starts with a dot is mangled into a Windows path list, so `git show refs/mr/88:.gitlab-ci.yml` fails with "ambiguous argument". Prefix those calls with `MSYS_NO_PATHCONV=1`.

Read every changed file in full when the MR is small. When it is large, read the files
carrying the logic in full and skim the mechanical ones. Then grep for callers of anything
whose signature, return value, or contract moved — the breakage a diff cannot show is
almost always at a call site the MR never touched.

**Use `base_sha` from the script's header, never `git merge-base`.** A local `origin/main`
is only as fresh as the last fetch, so the merge base computed locally can sit far behind
and hand you a diff containing other people's merged work. On a real MR here that turned a
2-file, 52-line change into a 21-file, 2592-line one.

## Step 3 — What to look for

Roughly in order of what is worth your attention:

1. **Correctness.** Does it do what it claims for the inputs it will actually see? Off-by-one,
   inverted conditions, unhandled `None`/empty/error returns, wrong operator precedence,
   resources never released, races between check and use.
2. **The claims in the description.** This author writes MRs that argue for themselves — a
   stated failure mode, a fix, often a table of verified results. Check the claims against
   the code rather than accepting them. Saying "confirmed at `file:line`" is a real review
   finding; so is "the description says X, the code does Y".
3. **Blast radius.** What else calls this? What relies on the old behaviour? Is there a
   migration, a config default, a deployed script that now disagrees with the code?
4. **Safe-direction failure.** When the change is wrong, does it fail toward refusing to act,
   or toward silent data loss? Guard rails that fail open are worth flagging even when the
   happy path is fine.
5. **Security.** Injection via interpolated shell or SQL, secrets in code or logs, authz
   checks skipped on a new path, user input reaching a filesystem or network call.
6. **Tests.** Does the MR's own stated bug have a test that would have caught it? A fix
   without a regression test is worth a P3, not a P1.
7. **Docs and specs.** When the MR touches a spec or runbook, do the prose and the code still
   agree with each other.

Then check the mechanics the header already gave you: a failing pipeline, conflicts, a
`detailed_merge_status` that is not `mergeable`, an unresolved thread, or draft state are all
reasons the MR is not ready regardless of how good the code is.

Prefer few, specific, defensible findings over a long list. For each one, be concrete about
the input or state that triggers it — if you cannot describe how it goes wrong, you are
guessing, and you should either verify it or drop it. Say so plainly when you are unsure
rather than dressing a hunch as a defect.

## Step 4 — Report

Use this shape:

```
# MR !88 — envctl: an environment whose work is merged must be releasable
One or two sentences on what the change actually does, in your own words from the code.

**Mechanics:** pipeline success · 2 files · mergeable · no unresolved comments

## Findings

### P1 — Release drops work: a rebased branch is let go with commits that exist nowhere else — `scripts/envctl.sh:134`
The concrete input or state, what happens, and why it matters.
Suggested fix, one line.

### P3 — No regression test for the squash-merge case — `scripts/envctl.sh:118`
...

## Verified
- Ancestry check really is two-dot, as the description claims — `scripts/envctl.sh:131`
- Spec table gains the containment row — `specs/multi-dev-environments.md:210`

## Not covered
Anything you could not check, and why.

## Verdict
MR !88 APPROVED
```

**Priority.** *P1* — breaks in production, loses data, opens a hole, or defeats the MR's own
stated purpose; must be fixed before this merges. *P2* — a real bug on a plausible path, or a
design problem that will cost more to undo later. *P3* — works, but an edge case, a missing
test, a misleading error. *P4* — naming, style, a typo. Drop the Findings section entirely
when there is nothing to report; do not pad it with low-priority items to look thorough.

Write each one as `P<n> — <short label>: <what actually goes wrong>`, then the file reference,
then the detail beneath. List them in priority order, P1 first. That opening line has to stand
on its own: someone skimming only the P1 lines should understand the risk without knowing the
codebase, so name the consequence in plain words rather than in function names. "Ownership
checks missing: seed, up and down can overwrite another task's claimed environment" lands;
"work_signals returns early" does not.

**The verdict line is the last line, on its own, exactly one of:**

```
MR !88 APPROVED
MR !88 CHANGES REQUESTED
```

Approve when there is no P1 and no P2, the pipeline is not failing, and no thread is
unresolved. P3s and P4s do not block — list them and approve anyway, since a review that
can never approve stops being read. If the only problems are mechanical (pipeline red, draft,
conflicts) say `CHANGES REQUESTED` and make clear in one line that the code itself is fine.

## Reviewing more than one MR

Given several targets, review each independently against its own base and give each its own
verdict line. Do not let a finding in one MR colour the verdict of another.
