#!/usr/bin/env python3
"""Has anything under `.agents/` or `.claude/` been edited since it was vendored?

    python3 .agents/check.py [<repo>]

Exits 1 and names the files if so, 0 if not.

**It reads only `MANIFEST.json` and the files beside it.** No network, no
`agent-standards` checkout, nothing to install beyond Python. That is the whole
point: a CI runner, a pre-commit hook and a server tree can all ask the
question, and none of them has this repo's source sitting at a known path.

`bin/agents-sync.py` imports `content_hash` and `edited` from this file rather
than keeping its own copy, so the answer cannot differ between the machine that
wrote the manifest and the machine checking it.

If this reports a file, the fix is not to edit it back: change the rule in
`agent-standards`, open a merge request there, and sync. `git checkout --` on
the named path restores the vendored copy in the meantime.
"""
import hashlib
import json
import pathlib
import sys

MANIFEST = ".agents/MANIFEST.json"


def content_hash(data):
    """Text hashed with LF endings, so the two machines agree about one commit.

    The workstation is Windows and v30 is Linux. Hashing raw bytes reports every
    text file as edited on whichever machine did not write it, which would make
    this check useless precisely where it is most useful.
    """
    if b"\x00" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def edited(repo):
    """Vendored paths that no longer match the manifest, sorted. [] if none."""
    path = repo / MANIFEST
    if not path.exists():
        return []
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return [dest for dest, want in sorted(manifest.get("files", {}).items())
            if not (repo / dest).is_file()
            or content_hash((repo / dest).read_bytes()) != want]


def main(argv):
    repo = pathlib.Path(argv[1] if len(argv) > 1 else ".").resolve()
    if not (repo / MANIFEST).exists():
        # A repo that has not adopted the shared rules is not a failure.
        print("%s: nothing vendored here (%s missing)" % (repo, MANIFEST))
        return 0
    bad = edited(repo)
    for dest in bad:
        print("EDITED  %s" % dest)
    if bad:
        print("\nThese are vendored from agent-standards and are not edited here.")
        print("Change the rule there and sync. To restore these copies:")
        print("    git checkout -- %s" % " ".join(bad))
        return 1
    print("%s: vendored files unchanged" % repo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
