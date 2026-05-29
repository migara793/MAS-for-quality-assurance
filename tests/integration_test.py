import asyncio
from agent import MLOpsHooks
from tools.mcp_config import get_mcp_tools

async def test_agent_calls_tool():
    tools = await get_mcp_tools()
    assert len(tools) > 0
    # Assuming the first tool is a file system tool and is always present.
    print("Successfully fetched tools.")


async def main():
    await test_agent_calls_tool()

if __name__ == "__main__":
    asyncio.run(main())
