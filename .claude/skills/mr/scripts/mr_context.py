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


def parse_target(target):
    """'!88' | '88' | 'MR 88' | full MR URL  ->  (iid, repo_url_or_None)"""
    t = target.strip()
    m = re.match(r"^(https?://[^\s]+?)/-/merge_requests/(\d+)", t)
    if m:
        return m.group(2), m.group(1)
    m = re.search(r"(\d+)", t)
    if not m:
        sys.exit("Cannot read an MR number from %r. Use !88, 88, or the MR URL." % target)
    return m.group(1), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="!88, 88, or a merge request URL")
    ap.add_argument("outdir", help="directory to write the context bundle into")
    args = ap.parse_args()

    iid, repo_url = parse_target(args.target)
    # glab's short --repo group/project form resolves against the DEFAULT host and 404s on
    # self-hosted instances, so when we were given a URL we pass the URL through verbatim.
    repo_flag = ["--repo", repo_url] if repo_url else []

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
    discussions = json.loads(run(api("discussions")).stdout)
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
    local = False
    inside = run(["git", "rev-parse", "--is-inside-work-tree"], check=False)
    if inside.returncode == 0 and inside.stdout.strip() == "true":
        remote = run(["git", "remote", "get-url", "origin"], check=False).stdout.strip()
        if project.split("/")[-1].lower() in remote.lower():
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
