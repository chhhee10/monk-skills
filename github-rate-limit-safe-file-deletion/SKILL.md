---
name: github-rate-limit-safe-file-deletion
description: "Use when deleting GitHub files or cleaning up branches from merged pull requests, especially after `429 Too Many Requests: API rate limit exceeded` or `malformed_json` errors."
monk:
  source_sessions: [01m3e8h9jna6h4m8b7s95v8fkf, 01m3e9750c0qr9avwxmcz0jryh, 01m3e9j52pfjn0maq94z3687yg, 01m3e9mddkp2dqh8tf7z1w16r6]
  fault_types: [rate_limit, malformed_json]
  verified: true
  win_rate: 2
  version: 1
---
1. Before deleting a file, obtain approval with `ask_user_question`; use `get_tool_info` to confirm the inputs for `get_file_contents` and `delete_file`, and use `list_tools` and `get_tool_info` to check branch-listing and branch-deletion tool schemas.
2. For file deletion, call `get_file_contents` with `call_tool` to fetch the target file and current SHA, then call `delete_file` with that SHA, the required commit message, and branch inputs. After a cooldown, fetch the file again if needed so the SHA is current.
3. For branch cleanup, inventory branches with `list_branches` and pull requests with `list_pull_requests(state=all)`, requesting PR number, head, base, and merged status. Preserve the default and protected branches, branches with open or unmerged work, and branches with ambiguous status.
4. If a PR's status is ambiguous, call `pull_request_read(method=get)` and confirm its merged status and head branch. Treat a branch as a deletion candidate only when its PR is confirmed merged and no preservation condition applies.
5. On `429 Too Many Requests: API rate limit exceeded`, do not retry immediately. Wait at least the stated `Retry after` duration or `retry_after` seconds using `wait_seconds`; for branch-cleanup calls, you may use `exec` to wait `retry_after` plus a small buffer. Retry only the affected call, no more than three times total.
6. On `malformed_json` or truncated output, do not use partial results. Check the affected tool's schema with `get_tool_info`, correct the request (for example, use a supported smaller `perPage`), and retry no more than three times total. For uncertain PR status, use `pull_request_read(method=get)` to verify it.
7. Before deleting branches, confirm with `list_tools` and `get_tool_info` that a supported branch-deletion tool exists. If `get_tool_info` reports `Tool 'delete_branch' not found`, do not substitute `delete_file` or `exec`; report the verified candidates and that no branches were deleted.
8. Delete only confirmed candidate branches with the supported branch-deletion tool. Verify file removal with `get_file_contents` or branch removal with `list_branches`; honor any rate-limit cooldown during verification and keep the three-attempt limit.
