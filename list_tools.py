import asyncio
import os
from tools.mcp_config import get_mcp_tools

async def list_all_tools():
    tools = await get_mcp_tools()
    for tool in tools:
        print(f"- {tool.name}")

if __name__ == "__main__":
    asyncio.run(list_all_tools())
