import os
import logging
from typing import List, Any
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from app_utils.env import config

# Configure logging
logger = logging.getLogger(__name__)

# INCREASED TIMEOUT FOR LOCAL/DOCKER EXECUTION
MCP_TIMEOUT = 180.0 

async def get_mcp_tools() -> List[Any]:
    """
    Initializes MCP tools via direct integration (Bypassing n8n).
    """
    all_tools = []
    
    # 1. Filesystem Tools
    try:
        fs_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                timeout=MCP_TIMEOUT,
                server_params=StdioServerParameters(
                    command="mcp-server-filesystem",
                    args=[os.getcwd()]
                )
            )
        )
        tools = await fs_toolset.get_tools()
        all_tools.extend(tools)
        logger.info(f"Loaded {len(tools)} Filesystem tools.")
    except Exception as e:
        logger.error(f"Failed to initialize Filesystem tools: {str(e)}")

    # 2. Shell Tools
    try:
        shell_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                timeout=MCP_TIMEOUT,
                server_params=StdioServerParameters(
                    command="mcp-shell",
                    args=[]
                )
            )
        )
        tools = await shell_toolset.get_tools()
        all_tools.extend(tools)
        logger.info(f"Loaded {len(tools)} Shell tools.")
    except Exception as e:
        logger.error(f"Failed to initialize Shell tools: {str(e)}")

    # 3. Playwright Tools
    try:
        playwright_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                timeout=MCP_TIMEOUT,
                server_params=StdioServerParameters(
                    command="playwright-mcp",
                    args=[]
                )
            )
        )
        tools = await playwright_toolset.get_tools()
        all_tools.extend(tools)
        logger.info(f"Loaded {len(tools)} Playwright tools.")
    except Exception as e:
        logger.error(f"Failed to initialize Playwright tools: {str(e)}")

    # 4. GitHub Tools
    if config.GITHUB_TOKEN:
        try:
            github_toolset = McpToolset(
                connection_params=StdioConnectionParams(
                    timeout=MCP_TIMEOUT,
                    server_params=StdioServerParameters(
                        command="mcp-server-github",
                        args=[],
                        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": config.GITHUB_TOKEN}
                    )
                )
            )
            tools = await github_toolset.get_tools()
            all_tools.extend(tools)
            logger.info(f"Loaded {len(tools)} GitHub tools.")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub tools: {str(e)}")
    else:
        logger.warning("GITHUB_TOKEN not found. GitHub MCP tools will not be available.")

    logger.info(f"Total direct MCP tools active: {len(all_tools)}")
    return all_tools

def filter_tools_by_name(all_tools: List[Any], keywords: List[str]) -> List[Any]:
    """
    Filters the discovered tools based on role-specific keywords.
    """
    return [t for t in all_tools if any(k.lower() in t.name.lower() for k in keywords)]
