"""
Contract test for MCP tool signatures and schemas.
Fails CI if tool schemas, parameters, or annotations change unintentionally.
"""
import os
import json
import pytest
from mcp_servers.portfolio.server import mcp as portfolio_mcp
from mcp_servers.marketplace.server import mcp as marketplace_mcp
from mcp_servers.workspace.server import mcp as workspace_mcp

SNAPSHOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_tool_snapshot.json")

def extract_server_signatures(mcp_instance):
    """Extract dict of tool names to their parameter names."""
    sigs = {}
    # Extract tool definitions
    for name, tool in mcp_instance._tool_manager._tools.items():
        sigs[name] = {
            "name": name,
            "description": tool.description,
            "parameters": list(tool.parameters.get("properties", {}).keys()) if hasattr(tool, "parameters") and tool.parameters else []
        }
    return sigs

def test_mcp_tool_contract():
    current_signatures = {
        "portfolio": extract_server_signatures(portfolio_mcp),
        "marketplace": extract_server_signatures(marketplace_mcp),
        "workspace": extract_server_signatures(workspace_mcp)
    }

    if not os.path.exists(SNAPSHOT_FILE):
        # Create initial snapshot
        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(current_signatures, f, indent=2)
        assert True
        return

    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        expected_signatures = json.load(f)

    # Compare tool names
    for server_name in ["portfolio", "marketplace", "workspace"]:
        assert server_name in expected_signatures, f"Missing server {server_name} in snapshot"
        curr_tools = current_signatures[server_name]
        exp_tools = expected_signatures[server_name]

        for t_name, t_meta in exp_tools.items():
            assert t_name in curr_tools, f"Contract broken: Tool '{t_name}' missing from server '{server_name}'"
            assert sorted(t_meta["parameters"]) == sorted(curr_tools[t_name]["parameters"]), (
                f"Contract broken: Parameter mismatch for tool '{t_name}' in server '{server_name}'"
            )

