---
name: mcp-call-tool-discovery-quirk
description: "Use when `call_tool` returns “Tool 'list_tools' is not allowed” or “Unknown tool: list_tools” while discovering MCP tools."
monk:
  source_sessions: [01m3e9683xzrnb55a3ycqkcq8j, 01m3e8frgznjetewr1hd2s7fez]
  fault_types: []
  verified: false
  win_rate: null
  version: 1
---
1. Call `list_tools(mcp_server=...)` directly to discover available tools; do not invoke `list_tools` through `call_tool`.
2. Use `get_tool_info(mcp_server=..., tool_name=...)` to check the arguments for the specific tool you plan to invoke.
3. Call `call_tool` with that discovered tool name and its documented input, rather than using `call_tool` for tool discovery.
4. If the discovery call fails, correct the tool name or invocation method before retrying; do not repeat the same failing `call_tool` request.
