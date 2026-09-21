# Git and merge-request workflow

Shared across every repo. The repo's own `AGENTS.md` wins where it disagrees — the GitHub
repos (`totalcmd-plugin-sftp`) substitute `gh` and "pull request" throughout.

## "GitLab" always means <https://gitlab.evo21.ch>

The self-hosted instance on `evo21-v10`, never `gitlab.com`. Everything in this file — every
`glab` invocation, every merge-request number, the protected `main`, the `ai-reviewer` bot —
is on that host and nowhere else. Practically:

- Clone over `ssh://git@gitlab.evo21.ch:5023/<group>/<repo>.git`. Port **5023**, not 22.
- `glab` picks the host up from the repo's own remote, so **run it inside the checkout**. Run
  from anywhere else and it silently targets `gitlab.com` and fails on an unrelated account.
- It is GitLab **CE**: no Duo, no built-in AI review, no group-level webhooks. That is why the
  reviewer in `review.md` is a bot user plus a per-project webhook rather than a feature.

## What the server enforces, and what is only convention

Know which is which: one fails loudly, the other depends on you. On a project set up from
`agent-standards/gitlab/settings.json`, GitLab itself rejects a push to `main` or `release/*`,
a force-push to either, and a `v*` tag from a non-Maintainer; and it refuses a merge while any
thread is open. Merging is Maintainer-only, so an agent running as a Developer cannot merge at
all — which is what makes the go-ahead in this file a rule rather than a promise.

Everything else here is convention, held up by the agent following it: one merge request per
branch, the branch prefixes, resolving a thread only after the fix is pushed, and the report
you end on. If a project has not had those settings applied, *all* of it is convention —
`python3 bin/project-settings.py check <project>` says which.

## Branches

- **Never commit straight onto `main`.** `main` is a protected branch on GitLab, push set to
  *no one* — a direct push is rejected by the pre-receive hook, whatever your role. Commit on
  a feature branch and push that.
- Match the prefixes the repo already uses; across these repos that is `fix/`, `feat/`,
  `docs/`, `chore/`, `infra/`. Check `git branch -r` rather than inventing one.
- **Several agents can be working in the same repo, and even the same branch, at once.**
  Finding unrelated modified or untracked files in the working tree — or a file you are
  editing changing on disk between reads — is expected, not a sign something broke. Don't
  revert or "clean up" changes you didn't make; touch only what your own task requires, and
  commit only that.
- **Commit messages are long and explain the reasoning**, not just the change. Read recent
  commits before writing one. End with the `Co-Authored-By:` trailer the repo uses.

## The lifecycle

**branch → commit → push → MR → REVIEW → CONFIRMATION → merge.** Never collapse those last
three steps into one.

- **Open the merge request when the task is done** — committed, pushed, your own checks
  passing — without being asked. Finishing the task is itself the request for review.
- **One MR per branch.** If the branch already has an open one — a second round of work, or
  another agent got there first — `glab mr create` aborts with "another open merge request
  already exists". Push, then update the existing description, and say in the status line
  that it moved.
- Once opened, treat it as awaiting human review. **Do not merge because CI is green** or
  because you judge the change safe. A human has to actually look at it.
- **Only merge after that human tells you, in this conversation, that they have reviewed it
  and it is ready** — an explicit go-ahead for the merge step specifically. Nothing upstream
  counts: not the task that produced the branch, not the MR having opened by itself, and not
  "open an MR so I can look at it", which asks for a look and not a merge. That go-ahead is
  the one human gate left in this workflow, which is why it is never inferred.
- Every message about one of your MRs ends with the status line from `communication.md`.

## `glab` is the tool — never the web UI, never a browser

Never the web UI: the CLI leaves a record of what an agent did. And `gh` is the wrong CLI
here however familiar it looks — the remote above is GitLab, not GitHub.

    glab mr create -s <branch> -b main -t "<title>" -d "$(cat /tmp/mr.md)" --yes
    glab mr view <n>                            # state, description, pipeline
    glab mr view <n> --comments                 # the review, once it lands
    glab mr note create <n> -m "<text>" --resolvable=false   # a comment on the MR
    glab mr update <n> -d "$(cat /tmp/mr.md)"   # after pushing more commits
    glab mr merge <n> --yes

Write the description to a file and pass `-d "$(cat ...)"` rather than typing it inline: it
is several paragraphs and a table by the time review is reached, and the shell is where that
formatting gets eaten. `--yes` skips the confirmation prompt, which an agent cannot answer.

## Initiative, and where it stops

Between tasks, keep improving the repo rather than waiting: fix what is fragile, delete what
is idle, tighten what is untested. Two limits:

- **Ask before anything irreversible or outward-facing** — deleting data, changing what a
  running system measures, exposing a port, and anything touching a live host —
  `ansible-playbook`, `docker compose`, a restart, an edit to a server checkout (`infra.md`).
  Committing and pushing a feature branch is not on that list, and neither is opening the
  merge request that finishes it. **Merging is.** Initiative stops at the merge.
- **Say what changed**, briefly. Silent improvements are indistinguishable from nothing
  happening.

## Where a finding goes

- **A defect found while working or operating the system** goes in the repo's tracker file
  where it has one (`FINDINGS.md` in auto-trader and alma-wordpress), dated from the
  evidence — not from your own clock, because containers log UTC and the machine you are
  driving from often is not. Write it down before fixing it; fixing without recording is how
  the same bug gets rediscovered later with no memory of the first time.
- **A code-review finding goes in the merge request, as a comment on the line it is about**,
  and never in the tracker. The reviewer is usually a different agent on a different machine,
  often without push rights — commenting on the diff is both the whole of what it can do and
  where the finding is actually actionable. Never hold up a review waiting for a tracker
  entry the reviewer was never able to write.

## `session-context/` (opt-in — auto-trader today)

Some repos keep per-branch working notes, so a branch picked up cold carries more than its
diff. Where a repo has the folder, "save context" means write or update
`session-context/<branch-name>.md` and commit it there; that repo's `AGENTS.md` has the rules.
