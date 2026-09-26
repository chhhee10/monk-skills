---
name: call-tool-http-429-retry-after
description: Use when `call_tool` returns `429 Too Many Requests` or `API rate limit exceeded` while calling a GitHub tool.
monk:
  source_sessions: [01m3egzxe166qxn1xhm38t33vg, 01m3eh1eb5ge9vj6s4wjw5cnzm, 01m3eh3t3ywk0ttj3yce80gats, 01m3eh5cks9mnfpnbjz61dg5kk]
  fault_types: []
  verified: true
  win_rate: 2
  version: 1
---
1. Read the `retry_after` value in the `call_tool` error; do not immediately repeat the failed call.
2. Call `monk-chaos.wait_seconds` for at least the specified number of seconds, giving the rate limit as the reason.
3. After the wait, retry the same `call_tool` request once with the original inputs.
4. If the retry returns another 429, follow its new `retry_after` value before trying again; make no more than three attempts total.
5. If the error has no `retry_after` value or attempts continue to fail, stop and report the rate limit rather than retrying without a wait.
