# Reporting: write so the owner understands it

Shared across every repo. The repo's own `AGENTS.md` wins where it disagrees.

**This is the rule that gets broken most often, so it comes first.** The owner is not a
specialist in whatever this repo does. They are paying for work they can act on, and an
explanation they cannot follow is not finished work — it is a draft they have to decode. If
they have to ask what something means, that was a writing failure, not a gap in their
knowledge.

- **Explain every specialist word the first time it appears in a message.** Inline, in the
  sentence, in six words or fewer. Not by linking to a glossary. If it cannot be explained in
  six words it probably should not be in the message. Repos that carry a list of their own
  jargon put it in their own `AGENTS.md`.
- **Convert units into things with a size.** Not "9.2bp" → "about a tenth of a percent". Not
  "p99 latency 2.4s" → "one request in a hundred takes long enough to look broken".
- **Say what it means before saying what it is.** Lead with the consequence for them, then the
  mechanism if they want it.
- **Prefer a short answer.** A long report with five headings reads as thorough to an agent and
  as homework to them. If the answer is three sentences, write three sentences. The repo's
  running-record file, where it has one, exists exactly so that messages can be short.
- **Numbers in a table beat numbers in a paragraph**, but only with at least three of them
  sharing a shape.
- **Never bury a bad result.** If something is broken, wrong, or was your mistake, that goes in
  the first line, plainly, with no cushioning.

## Verify before reporting, and report what actually happened

- Do not say something works because the code looks right. Run it and look at the output.
- If a test fails, show the failure. If a step was skipped, say which one and why.
- When a number changes a conclusion, verify it through a second route before reporting it.

## The status line

**End every message about one of your merge requests with a status line, and write nothing
after it.** The question the owner is actually asking is "is it ready for me to look at
again?", and they should not have to read four paragraphs of findings to work it out.

    READY: !88 @ 4b0a4d7 · https://gitlab.evo21.ch/interpid/auto-trader/-/merge_requests/88

Four statuses, and no others — fixed words, so the line can be skimmed rather than read:

| status | means |
|---|---|
| `READY` | pushed, nothing known outstanding, your own checks pass |
| `NOT READY` | still working — the clause says what is missing |
| `NEEDS FEEDBACK` | blocked on a decision or something only the owner can do — the clause says what |
| `MERGED` | landed — `@` is the merge commit |

- **The URL goes in BARE, at the end — not as a markdown link.** `[!88](...)` was tried and
  reverted on 2026-09-20 for a concrete reason: the owner copies these lines out, and copying
  rendered markdown takes the visible text and drops the href, so the URL disappears. A bare
  URL survives copy-paste into anything. `!88` alone is a reference, not a destination.
- **Always the exact commit.** "Ready" is a claim about one SHA; push again and the earlier
  "ready" is void, so say it again with the new one.
- **A clause is required for `NOT READY` and `NEEDS FEEDBACK`**, saying what is missing:
  `NEEDS FEEDBACK: !90 @ a1b2c3d · pick a port band before I write the .env · <url>`.
- **Never write `READY` while a known finding is unaddressed, or before pushing.** A finding
  deliberately not fixed is `NEEDS FEEDBACK` with the reason — not `READY` with a caveat
  hidden further up. The word is only worth anything if it is never stretched.
- On the GitHub repos the same line uses `#88` and the pull-request URL. Nothing else changes.

## Give the URL

- **When you report a change that can be looked at, give the full URL of the page it changed**,
  deep rather than the root. A bare domain is not enough when the change is three clicks in.
- **If the change cannot be seen anywhere, say that explicitly** and say what you checked
  instead. Silence about the URL reads as "not checked".
