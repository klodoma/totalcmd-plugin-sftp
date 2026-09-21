#!/usr/bin/env python3
"""Gather everything needed to review a GitLab merge request.

Writes a context bundle to an output directory and prints a summary.
Read-only: every call here fetches, nothing mutates the MR.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if check and p.returncode != 0:
        sys.exit("FAILED: %s\n%s%s" % (" ".join(cmd), p.stdout, p.stderr))
    return p


def api_list(command):
    """Read every page, including when a full page is followed by an empty one."""
    items = []
    page = 1
    while True:
        paged = list(command)
        paged[2] += "?per_page=100&page=%d" % page
        batch = json.loads(run(paged).stdout)
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def remote_id(url):
    """Any git remote spelling -> 'host/group/repo', lowercased. None if unrecognised.

    Written to compare two remotes for identity, so the parts that can differ
    between spellings of the same repo are dropped: the scheme, a user prefix, the
    port (git-over-ssh is 5023 here while the web URL is 443) and a `.git` suffix.
    """
    u = (url or "").strip()
    if not u:
        return None
    u = re.sub(r"\.git$", "", u)
    m = re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*://(?:[^@/]+@)?([^/:]+)(?::\d+)?/(.+)$", u)
    if not m:  # scp-style: git@host:group/repo
        m = re.match(r"^(?:[^@/]+@)?([^:/]+):(.+)$", u)
    return ("%s/%s" % (m.group(1), m.group(2))).lower() if m else None


def parse_target(target):
    """'!88' | '88' | 'MR 88' | 'group/repo!88' | full MR URL -> (iid, repo_or_None).

    Every form is anchored, and an unrecognised one is refused rather than
    guessed at. The earlier version searched for the first run of digits
    anywhere in the string, which read `evosys21/guitar-tabs!28` as merge
    request 21 -- a real merge request, in the *current* project, reviewed
    without a word about the one that was asked for. `commands.md` documents
    `group/repo!56` as the way to cross projects, so it has to be the thing
    that happens.
    """
    t = target.strip()

    m = re.match(r"^(https?://\S+?)/-/merge_requests/(\d+)", t)
    if m:
        return m.group(2), m.group(1)

    m = re.match(r"^([\w.\-]+(?:/[\w.\-]+)+)\s*!\s*(\d+)$", t)
    if m:
        return m.group(2), m.group(1)

    m = re.match(r"^(?:MR\s*)?!?\s*(\d+)$", t, re.IGNORECASE)
    if m:
        return m.group(1), None

    sys.exit("Cannot read a merge request from %r.\n"
             "Use 88, !88, group/repo!88, or the full merge request URL." % target)


def project_url(path):
    """'group/repo' -> a full URL on the host this checkout's origin points at.

    glab's short `--repo group/project` form resolves against the DEFAULT host and
    404s on a self-hosted instance, so the host has to come from somewhere. The
    session is rooted in one repo on one instance (`commands.md`), so that repo's
    origin is the right place to take it from -- and if there is no origin to ask,
    say so rather than quietly falling back to gitlab.com.
    """
    remote = run(["git", "remote", "get-url", "origin"], check=False).stdout.strip()
    ident = remote_id(remote)
    if not ident:
        sys.exit("%r names a project but not a host, and this directory has no "
                 "origin to take one from. Pass the full merge request URL." % path)
    return "https://%s/%s" % (ident.split("/")[0], path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="!88, 88, or a merge request URL")
    ap.add_argument("outdir", help="directory to write the context bundle into")
    args = ap.parse_args()

    iid, repo = parse_target(args.target)
    # glab's short --repo group/project form resolves against the DEFAULT host and 404s on
    # self-hosted instances, so a URL is passed through verbatim and a bare group/repo is
    # given the host of this checkout's origin.
    if repo and not repo.startswith("http"):
        repo = project_url(repo)
    repo_flag = ["--repo", repo] if repo else []

    os.makedirs(args.outdir, exist_ok=True)

    def write(name, text):
        with open(os.path.join(args.outdir, name), "w", encoding="utf-8") as f:
            f.write(text)

    mr = json.loads(run(["glab", "mr", "view", iid, "-F", "json"] + repo_flag).stdout)
    write("mr.json", json.dumps(mr, indent=2))
    write("description.md", (mr.get("description") or "").strip() + "\n")

    project = urllib.parse.urlparse(mr["web_url"]).path.split("/-/merge_requests/")[0].strip("/")
    enc = urllib.parse.quote(project, safe="")

    def api(path):
        return ["glab", "api", "projects/%s/merge_requests/%s/%s" % (enc, iid, path)] + repo_flag

    diff = run(["glab", "mr", "diff", iid] + repo_flag).stdout
    write("diff.patch", diff)

    changes = json.loads(run(api("changes")).stdout)
    discussions = api_list(api("discussions"))
    write("discussions.json", json.dumps(discussions, indent=2))

    # GitLab returns bookkeeping ("added 1 commit", "changed the description") as notes too.
    # Only human notes are review context, and a standalone human comment arrives with
    # individual_note=True, so system-vs-human is the distinction that matters here rather
    # than threaded-vs-standalone.
    human = []
    for d in discussions:
        notes = [n for n in d.get("notes", []) if not n.get("system")]
        if not notes:
            continue
        head = notes[0]
        loc = (head.get("position") or {}).get("new_path")
        state = "unresolved" if any(n.get("resolvable") and not n.get("resolved")
                                    for n in notes) else "resolved"
        body = "\n\n".join("**%s:** %s" % ((n.get("author") or {}).get("username"),
                                           (n.get("body") or "").strip()) for n in notes)
        human.append("## %s on %s [%s]\n\n%s" % (
            (head.get("author") or {}).get("username"), loc or "the MR", state, body))
    write("discussions.md", ("\n\n".join(human) or "No human comments on this MR yet.") + "\n")

    refs = mr.get("diff_refs") or {}
    base_sha = refs.get("base_sha")
    head_sha = refs.get("head_sha") or mr.get("sha")

    # Make the MR's commits readable locally without touching the working tree or any branch:
    # no checkout, no stash, nothing for the user to clean up afterwards. Only possible when
    # the current directory is the clone this MR belongs to.
    #
    # The identity test is the whole host and path, not the repo's basename. A
    # basename appearing anywhere in the origin URL also matches a fork, another
    # group's repo of the same name, and another instance entirely -- and the
    # failure is silent in the worst way: `refs/merge-requests/<iid>/head` almost
    # certainly exists in that other project too, so the fetch succeeds and the
    # header then sends the reviewer to read a different merge request's code
    # under the right number.
    local = False
    inside = run(["git", "rev-parse", "--is-inside-work-tree"], check=False)
    if inside.returncode == 0 and inside.stdout.strip() == "true":
        remote = run(["git", "remote", "get-url", "origin"], check=False).stdout.strip()
        here = remote_id(remote)
        mr_host = urllib.parse.urlparse(mr["web_url"]).netloc.split(":")[0]
        if here and here == ("%s/%s" % (mr_host, project)).lower():
            fetched = run(["git", "fetch", "-q", "origin",
                           "refs/merge-requests/%s/head:refs/mr/%s" % (iid, iid)], check=False)
            local = fetched.returncode == 0
            if local and base_sha:
                run(["git", "fetch", "-q", "origin", base_sha], check=False)

    files = []
    for c in changes.get("changes", []):
        flag = ("deleted" if c.get("deleted_file") else
                "new" if c.get("new_file") else
                "renamed" if c.get("renamed_file") else "modified")
        files.append("%-9s %s" % (flag, c["new_path"]))
    write("files.txt", "\n".join(files) + "\n")

    pipe = mr.get("head_pipeline") or mr.get("pipeline") or {}
    unresolved = sum(1 for t in human if "[unresolved]" in t)

    print("MR !%s  %s" % (iid, mr["title"]))
    print("project      %s" % project)
    print("state        %s%s" % (mr["state"], "  (DRAFT)" if mr.get("draft") else ""))
    print("author       %s" % (mr.get("author") or {}).get("username"))
    print("branch       %s -> %s" % (mr["source_branch"], mr["target_branch"]))
    print("squash       %s" % mr.get("squash"))
    print("conflicts    %s" % mr.get("has_conflicts"))
    print("merge status %s" % mr.get("detailed_merge_status"))
    print("pipeline     %s  %s" % (pipe.get("status", "none"), pipe.get("web_url", "")))
    print("discussions  %d human comment(s), %d unresolved" % (len(human), unresolved))
    print("diff         %d file(s), %d patch lines" % (len(files), diff.count("\n")))
    print("base_sha     %s" % base_sha)
    print("head_sha     %s" % head_sha)
    print("local refs   %s" % ("refs/mr/%s fetched" % iid if local
                               else "NOT available - review from diff.patch only"))
    print("url          %s" % mr["web_url"])
    print()
    print("bundle: %s" % os.path.abspath(args.outdir))
    print("  mr.json  description.md  diff.patch  files.txt  discussions.md")
    print()
    print("changed files:")
    for f in files:
        print("  " + f)
    if local:
        print()
        print("read whole files at the MR head:  git show refs/mr/%s:<path>" % iid)
        print("reproduce GitLab's exact diff:    git diff %s..refs/mr/%s" % (base_sha[:12], iid))


if __name__ == "__main__":
    main()
