---
name: github-safe-delete-merged-pr-branches
description: Use when deleting repository branches whose pull requests are merged, while preserving the default branch and any branch with unmerged work.
monk:
  source_sessions: [01m3eh5cks9mnfpnbjz61dg5kk]
  fault_types: [permission_denied, rate_limit, server_error]
  verified: true
  win_rate: 1
  version: 1
---
1. Call list_tools, then get_tool_info for list_branches, list_pull_requests, and delete_branch to confirm the available inputs before acting.
2. Use call_tool with list_pull_requests to identify branches whose pull requests are confirmed merged; include closed pull requests if the tool supports that state.
3. Use call_tool with list_branches to verify each candidate branch still exists and is not the default branch; do not delete a branch with unmerged work or uncertain status.
4. If a call returns `403 Forbidden: Resource not accessible by personal access token`, do not retry unchanged or infer branch safety from partial results. Stop branch deletion and request the required repository access through the authorized process.
5. If a call returns `429 Too Many Requests: API rate limit exceeded. Retry after N seconds`, call wait_seconds for at least N seconds, then retry only the rate-limited call.
6. If a call returns `500 Internal Server Error: the upstream server encountered an error.`, wait briefly with wait_seconds and retry that call once; if it still fails, stop rather than deleting based on incomplete information.
7. Call delete_branch only for branches verified as merged, present, and not the default branch; inspect each result and stop if the response leaves the branch state uncertain.
