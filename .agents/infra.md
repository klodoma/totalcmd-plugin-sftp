# The servers, and how to reach them

Shared across every repo — only what you need before touching anything, whichever repo you
are in. Verified 2026-09-19.

**Server configuration lives in the `hosting` repository, which sets up both hosts with
Ansible.** Anything about how a server itself is built — nginx, users, certificates, systemd
units, a deployed service, a port — is a change to a template or inventory file there, applied
by running a playbook. **Never hand-edit a file on a host**: the next playbook run reverts it,
and the change is then lost with no trace of why it was made. That repo's `AGENTS.md` says how
to run one, and `hosting/docs/services-and-ports.md` is the service and port map. No other
repo needs to know more than this.

## Two hosts

Both Ubuntu, sshd on **5022**. `*.evo21.ch` is a **wildcard** record pointing at v30, so a
name resolving is never proof it is configured.

| Host | Role |
|---|---|
| `evo21-v30` | Web + applications: the WordPress sites, auto-trader prod **and** dev, the shared databases |
| `evo21-v10` | Platform: GitLab, Bitwarden, Authentik |

| Alias | User | Use it for |
|---|---|---|
| `ssh v30` | `gru` | Admin reads — nginx config, `ss`, `systemctl` |
| `ssh v30-dev` | `devuser` | App checkouts, `hosting`, the `docker` CLI |
| `ssh v30-wwwdev` | `wwwevo21dev` | The dev WordPress docroots |
| `ssh v30-wwwprod` | `wwwevo21prod` | Prod static docroots |

Root on v30, and v10 over ssh, are **not reachable from the workstation** — ask rather than
accepting a host key. `sudo` as `wwwevo21dev` is denied too, so WordPress database
credentials cannot be read that way.

## Where the code lives

| Pattern | What it is |
|---|---|
| `/home/devuser/<project>` | **Production** stack, bind-mounted by its containers |
| `/home/devuser/<project>-dev[N]` | Dev and pool environments |
| `/vhosts/www/<env>/<site>` | WordPress docroot, often a live git checkout |
| `/srv/<service>` | Ansible-deployed sidecars |

**Editing a server checkout is a deployment.** For a WordPress site, editing the checkout
*is* publishing; `/home/devuser/<project>` is production and its containers run whatever is
on disk. Confirm before `git pull`, `docker compose up`, a branch switch or a restart —
switching branches in a live tree has already taken `trader.evo21.ch` down. Never edit one
to "try something".

Two traps: **container names can invert what you expect** (auto-trader's `auto-trader-*`
containers are production, `trader-dev-*` are development), and **a live tree's `AGENTS.md`
is whatever the deployed commit had**, possibly far behind `main` — read it from a dev tree
or `git show origin/main:AGENTS.md`.

## Ports

nginx on `:80`/`:443` is the only public listener; everything else binds `127.0.0.1`. Dev
ports follow `9·A·PP` — app digit, component slot. Shared databases are `infra-postgres`
`5432`, `infra-mariadb` `3306`, `infra-redis` `6379`. Trust a live `ss -ltn` over any written
scheme, and read `hosting/docs/services-and-ports.md` for the rest.

**Docker publishes on every interface** and writes its own firewall rules, so a published
port is reachable from the host's public address whatever `ufw` says. Bind `127.0.0.1:`
unless the port is genuinely meant to be public.

GitLab is self-hosted on v10 — see `workflow.md`.

## The devauth gate

Dev vhosts sit behind a password gate with **four independent ways in**, each rotatable
without disturbing the others: a `devauth` cookie (works everywhere, including the trader
vhosts), an `X-Devauth-Bypass` header, an IP allowlist, and a `?devkey=` magic link (those
three are WordPress vhosts only). Tokens are read from the inventory when needed and never
written into a doc — see `secrets.md`.

```bash
curl -sS -H "X-Devauth-Bypass: $BYPASS_TOKEN" https://alma.dev.evo21.ch/   # WordPress
curl -sS -b "devauth=$DEVAUTH_TOKEN" https://trader.dev.evo21.ch/          # trader
```

**The office IP is allowlisted**, so from the workstation every request already bypasses the
gate and testing it from here gives a false pass. Test from v30's own loopback, which is not
allowlisted. Full mechanics: `hosting/ansible/README.md`.

## Local checkouts are for review — the server is for running

They exist so code can be read, reviewed, edited and rendered in a browser pane. They are not
where the systems run: data, APIs, auth and the nginx gate are not there, so a local render
is **a look at the components, not a working system**.
