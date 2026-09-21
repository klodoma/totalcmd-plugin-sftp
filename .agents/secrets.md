# Secrets

Shared across every repo. The repo's own `AGENTS.md` wins where it disagrees.

## A secret's value never leaves the place it is stored

Not into a message, a log line, a commit — its diff *or* its message — an MR comment, a
`session-context/` file, or a doc.
**Name the key, never print what it is set to** — `DIRECTUS_EDITOR_TOKEN`,
`webserver_dev_auth_token`. Read a value at the moment you need it rather than copying it
somewhere, so that rotating it cannot leave a stale copy behind.

**Redacting afterwards does not undo it.** A pushed commit and a posted comment are already
readable by everyone with repo access. The fix is to rotate the credential, not to edit the
text — so say so immediately rather than quietly deleting the line.

## Rotating some secrets breaks live services

`authentik_secret_key`, database passwords, anything an already-encrypted store was sealed
with. Re-running the playbook does not undo it. **If a task looks like it would regenerate
one, stop and ask.**

## `.env.example` documents which keys exist, not what they are

Never add an example value to a template. Each repo's git-ignore rules for secret files are
deliberate — do not commit around them, and see that repo's own `AGENTS.md` for which paths
they are and how its playbooks or containers are given the values.
