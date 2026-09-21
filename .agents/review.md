# The GitLab AI reviewer, and how to work a review round

`ai-reviewer` is a bot user on `gitlab.evo21.ch`. It reads the merge request's full diff plus
this repo's own conventions files, then posts a summary note and one resolvable thread per
finding. It is **advisory**: its approval is not the human go-ahead, and `workflow.md`'s merge
gate is unchanged.

**It triggers on exactly two things**: being *added* as Reviewer, and a comment whose first
word is `/review`. Pushing commits does not trigger it. Re-saving the reviewer list when it is
already assigned does nothing. It never resolves a thread — that is the author's job.

The short forms in `commands.md` compile to this: `~AIF` is steps 3–5, and `~AIR` is the
request plus the read — step 1 on the first round, step 6 on every later one, then 2–3 either way.

## 1. Ask for the review

```bash
glab mr update <n> --reviewer +ai-reviewer                  # first round only
MSYS_NO_PATHCONV=1 glab mr note create <n> -m "/review" --resolvable=false  # every later round
```

Both additions to that second line are load-bearing, and both were learned by it failing quietly:

- **`MSYS_NO_PATHCONV=1`, on Git Bash for Windows.** Without it the shell rewrites the leading
  slash into a filesystem path and the comment posts as `C:/Users/.../review`. The bot never
  fires, nothing reports an error, and you wait out the timeout for a review nobody requested.
- **`--resolvable=false`.** `glab mr note create` opens a *discussion thread* by default, so
  without it your own `/review` becomes an open thread — the very thing the next round
  refuses to run on.

`glab mr note <n> -m` still works but is deprecated; `note create` is the current spelling.

## 2. Wait for it

It posts a placeholder note immediately — *"reviewing this merge request with …"* — and then
**edits that same note** into the result. A minute or two is normal.

**Poll the body of its latest note, not the note list.** Two things follow from the result
being an edit rather than a new note:

- **`created_at` never moves**, so a poller that filters on it waits forever for a note that
  has already arrived. Match on the body — the placeholder wording gone, a line beginning
  `**AI review** —` present — or compare `updated_at` against `created_at`.
- **The note count does not change either.** A new round edits the round's own placeholder;
  it does not append.

The line reads `**AI review** — openai/gpt-5.5`: the provider and model that actually
answered, so a thin review can be traced to which model wrote it. Today that is always
OpenAI, because the service ships with the fallback provider disabled — match the literal
`**AI review** —` prefix and treat what follows as information, not as a field to parse.

**Never send a second `/review` while one is running.** It is declined silently: nothing
appears on the merge request, and the silence is indistinguishable from the bot being down.

## 3. Read both surfaces

```bash
glab api "projects/:id/merge_requests/<n>/discussions?per_page=100"   # the threads
glab mr view <n> --comments                                           # the summary note
```

Threads carry the findings that could be anchored to an added (`+`) line — they are the
entries with `"type": "DiffNote"` and `"resolvable": true`, and their `id` is the
`discussion_id` you need later. **Findings that could not be anchored exist only in the
summary note**, under *"Findings that could not be anchored to a changed line"*, and a
rejected position gets its own extra note. Reading threads alone loses them.

**`per_page=100` is load-bearing, and it is a cap rather than "all".** Left at the default
the endpoint returns twenty discussions and puts the rest on the next page, silently: a
merge request with open blockers reads as clean, and nothing anywhere says a page was
skipped. Past a hundred, follow `x-next-page`, or let `glab api --paginate` do it. This has
already cost a round on `evo21/agent-standards!5` -- thirty-two discussions, two open
blockers on page two, reported as none.

**Where your count and GitLab disagree, GitLab is right.** The merge request carries
`blocking_discussions_resolved`, which is the server answering the same question from its
own records:

```bash
glab api "projects/:id/merge_requests/<n>" | python3 -c "import sys,json; print(json.load(sys.stdin)['blocking_discussions_resolved'])"
```

Check it against what you counted before saying a round is clean. That mismatch is what
caught the paging bug above, and it is cheap enough to be worth doing every time.

## 4. Answer every finding, in the thread it came from

Not as a new merge-request note: the finding and the answer belong on the line they are
about. Disagreeing is a legitimate answer — a bot reading a diff without the surrounding
context gets things wrong, and saying why beats a silent dismissal.

**If you are refusing, the reply is not enough.** The bot is sent the title, the conventions
files, the description and the diff — never the notes. Fixing a finding rewrites the diff, so
it stops coming back; refusing one changes nothing it reads, and the next round can raise it
again word for word. Put the reason where it will be read: **one line in the merge request
description** for a one-off, or in the repo's `AGENTS.md` when it is a standing fact — "`glab`
here is 1.118.0, so `note create` is current and `-m` is deprecated". The thread is for the
humans; the description is the only channel that survives to the next round.

```bash
glab api -X POST "projects/:id/merge_requests/<n>/discussions/<did>/notes" \
  -f "body=Fixed in <sha> — the guard now runs before the write."
```

`-f` takes the whole body, newlines and markdown included, and glab encodes it — so build
the argument in a script rather than a shell string, where backticks and apostrophes in the
reply get eaten. `--input` is the wrong tool here: it sends no content type and GitLab
answers 415.

## 5. Resolve — after the fix is pushed, never before

```bash
glab api -X PUT "projects/:id/merge_requests/<n>/discussions/<did>?resolved=true"
```

Name the commit in the reply first. A resolved thread with no reply is indistinguishable from
a finding that was waved away.

## 6. Ask for the next round

Only once every thread is answered:

```bash
MSYS_NO_PATHCONV=1 glab mr note create <n> -m "/review" --resolvable=false
```

Then report with the status line from `communication.md`.

## What its approval means

It approves at the head commit when a round is clean, and **withdraws approval** when a later
round finds something — so a green badge from round 1 says nothing after round 2.

**"No findings" is not the same claim as "approved".** It refuses to approve when any file was
skipped, or when the model's answer was malformed, and says which in a `Not approving:` line.
That line means *the review did not cover the whole merge request* — read it and repeat it to
the owner rather than reporting a clean review.

```bash
glab api "projects/:id/merge_requests/<n>/approvals"
```

## Traps

- **It has no memory between rounds.** Each round reviews the whole diff from scratch, with no
  knowledge of earlier comments. Anything not actually fixed comes back as a *new* thread
  rather than a reply on the old one, and it can raise something new on code that did not
  change. Threads accumulate across rounds — that is expected, not a malfunction.
- **Resolving tells the bot nothing.** Resolve for the humans reading the merge request.
- **A thread is not auto-resolved when its line changes.** A genuinely fixed finding keeps its
  thread open until you close it.
- **Nothing enforces "resolve everything before re-reviewing"** — `/review` fires whatever the
  thread state is. It is a convention, and following it is what keeps the merge request
  readable.
