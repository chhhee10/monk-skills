---
name: github-list-issues-429-recovery
description: "Use when `list_issues` returns `429 Too Many Requests: API rate limit exceeded` with a `retry_after` value."
monk:
  source_sessions: [01m3egzxe166qxn1xhm38t33vg]
  fault_types: [rate_limit]
  verified: false
  win_rate: null
  version: 1
---
1. Read the `retry_after` value from the `list_issues` error.
2. Call `monk-chaos.wait_seconds` for at least that many seconds before retrying; the wait cleared the fault in the observed case.
3. Retry `call_tool` with `tool_name=list_issues` and the original input after the wait.
4. If the retry still returns a rate-limit error, wait for its stated `retry_after` before trying again; do not make more than three attempts.
5. Skip immediate retries and avoid changing the issue filters just to work around the rate limit.
