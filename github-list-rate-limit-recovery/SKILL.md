---
name: github-list-rate-limit-recovery
description: "Use when monk-chaos.list_branches or monk-chaos.list_issues returns `429 Too Many Requests: API rate limit exceeded` and includes a retry-after duration."
monk:
  source_sessions: [01m3e9750c0qr9avwxmcz0jryh, 01m3e9j52pfjn0maq94z3687yg, 01m3e9mddkp2dqh8tf7z1w16r6]
  fault_types: [rate_limit]
  verified: false
  win_rate: null
  version: 1
---
1. Read the `retry_after` value in the error response; do not immediately repeat the failed request.
2. Call `monk-chaos.wait_seconds` for at least the requested number of seconds, then retry the same list call with its original arguments.
3. If the retry is rate-limited again, wait for the new `retry_after` duration before trying again; make no more than three retries.
4. Skip rapid repeated calls and unrelated tool discovery or alternate-server attempts; waiting for the stated cooldown worked.
