"""Minimal example of an LLM-style agent interacting with ChillMCP.

The script demonstrates how a Model Context Protocol client could call the
server that lives in :mod:`main`.  It uses FastMCP's convenience
``Client`` class with a stdio transport that launches ``main.py``.

Running the script will:

1. Connect to the MCP server exposed by ``main.py``.
2. List the available tools.
3. Trigger a ``take_a_break`` tool call and print the textual response.

The code is intentionally lightweight so it can serve as a reference snippet
for integrating the server into a larger LLM agent orchestration stack.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client


async def main() -> None:
    client = Client(Path(__file__).with_name("main.py"))
    async with client:
        tools = await client.list_tools()
        tool_names = ", ".join(sorted(tool.name for tool in tools))
        print(f"Available tools: {tool_names}")

        result = await client.call_tool("take_a_break")
        if result.content:
            print("--- Tool Response ---")
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
