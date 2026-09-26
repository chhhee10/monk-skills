---
name: machine-workspace
description: "Use before exploring this machine's files or answering questions about this machine, its workspace, local logs, data, databases, infra or cloud-cost exports, support tickets, access reviews or runbooks. Not for GitHub repos or the web."
monk:
  pinned: true
---
This machine has a shared workspace at `~/workspace`: the ops box of Ledgerly, a small billing SaaS in Bengaluru (code with git history, the billing database, AWS, IAM and helpdesk exports, logs, runbooks, notes).

1. Before exploring files or answering anything about "this machine", "the workspace", logs, data, infra, tickets, access or runbooks, run: `bash /opt/tf/skills/machine-workspace/setup.sh` (safe to repeat: once `~/workspace` is set up it leaves it alone)
2. Read `~/workspace/README.md` first; it maps every folder.
3. Explore like a careful engineer with `ls`, `find`, `grep`/`rg`, `cat`, `jq`, `sqlite3 ~/workspace/db/ledgerly.db`, `git -C ~/workspace/projects/ledgerly-api log`. Check facts in the files before you state them, and cite paths and numbers.
4. Rehearse anything that changes data on a copy first (`cp ~/workspace/db/ledgerly.db /tmp/rehearsal.db`).
5. Never run a destructive command from a runbook (delete, purge, drop, truncate, `rm`) without the user's approval. `exec` has no approval prompt, so ask with `ask_user_question`, naming exactly what will be removed, and run it only after a clear yes.
6. To restore a pristine workspace: `bash /opt/tf/skills/machine-workspace/setup.sh --reset` (wipes every change in `~/workspace`; ask first).
