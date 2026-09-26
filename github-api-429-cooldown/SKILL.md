---
name: github-api-429-cooldown
description: "Use when a GitHub operation through `call_tool` returns `429 Too Many Requests: API rate limit exceeded` or an `http_429` error."
monk:
  source_sessions: [01m3e8h9jna6h4m8b7s95v8fkf, 01m3e9683xzrnb55a3ycqkcq8j, 01m3e8frgznjetewr1hd2s7fez]
  fault_types: []
  verified: false
  win_rate: null
  version: 1
---
1. Call the intended GitHub operation with `call_tool` and the required inputs; use `get_tool_info` to check an operation's inputs, and do not use `list_tools` on a server where it returns `Tool 'list_tools' is not allowed`.
2. When the error includes `Retry after N seconds`, record the requested wait and do not repeat the rate-limited call before that cooldown expires.
3. After the cooldown, retry the same operation once; if it returns another 429, follow the new `Retry after` value before any further attempt.
4. Do not make more than three attempts for the same operation; if it still returns 429, stop and report the rate limit rather than repeatedly calling `call_tool`.
5. If other independent operations are needed, call them only when appropriate; a rate-limited request does not establish that every other operation will fail.
