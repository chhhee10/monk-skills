---
name: github-labeled-issues-rate-limit-cooldown
description: Use when listing open GitHub issues by label or creating an issue from a repository template, especially when a GitHub tool returns `429 Too Many Requests` or `API rate limit exceeded`.
monk:
  source_sessions: [01m3egzxe166qxn1xhm38t33vg, 01m3eh1eb5ge9vj6s4wjw5cnzm]
  fault_types: [rate_limit]
  verified: false
  win_rate: null
  version: 1
---
1. Call `list_tools` to discover the relevant GitHub tools, then call `get_tool_info` for `list_issues` or `issue_write` as needed to confirm their input schemas.
2. For an issue listing, call `call_tool` with `list_issues`, the repository owner and name, `state` set to `open`, and the requested label.
3. For issue creation, use `get_file_contents` to read the repository template and note every required section and listed label.
4. If a tool returns `429 Too Many Requests: API rate limit exceeded` with `retry_after`, call `wait_seconds` for at least that many seconds before retrying; use any new `retry_after` value on subsequent rate limits, and do not retry the same call more than three times.
5. If `get_file_contents` remains rate-limited, do not repeatedly call it or switch to `web_fetch` for the same raw file if that also returns 429; use `exec` with `curl -L --fail --silent --show-error` to fetch the public raw template instead.
6. Before creating the issue, prepare a title, content for every template section, and exactly the labels listed by the template; if required details are missing, use `ask_user_question` rather than inventing template-specific facts.
7. Create the issue by calling `issue_write` through `call_tool` with the create method, repository, title, completed template content, and exactly the template-listed labels.
8. For an issue listing, provide each returned issue’s number and a concise one-line summary.
