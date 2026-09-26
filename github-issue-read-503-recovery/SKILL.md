---
name: github-issue-read-503-recovery
description: "Use when the GitHub issue_read tool returns `503 Service Unavailable: the upstream server encountered an error`."
monk:
  source_sessions: [01m3eh3t3ywk0ttj3yce80gats]
  fault_types: [server_error]
  verified: false
  win_rate: null
  version: 1
---
1. Treat the `503` as a transient read failure; do not infer issue contents from the failed response.
2. Wait briefly, then retry `issue_read` once with the same owner, repository, and issue arguments.
3. If the retry succeeds, continue reading the remaining issues and verify each response before acting.
4. If it fails again, wait longer before another attempt; do not retry the same call more than three times total.
5. If reads still fail, stop actions that depend on the missing issue data and report which issues could not be verified.
6. Skip repeating unrelated searches or changing issue state to work around a failed read.
