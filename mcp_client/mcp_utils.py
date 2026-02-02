import logging
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
from pydantic import Field, create_model
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, Tool as McpToolDef
from langchain_core.tools import StructuredTool

logger = logging.getLogger(__name__)

# Dependency for MCP Session
async def get_mcp_session() -> AsyncGenerator[ClientSession, None]:
    """
    Creates a fresh MCP session for each request.
    Connects via SSE to the standalone MCP server.
    """
    mcp_url = "http://localhost:8001/sse"
    logger.info(f"Connecting to MCP Server at {mcp_url}...")
    
    try:
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    except Exception as e:
        logger.error(f"Failed to connect to MCP Server: {e}")
        raise HTTPException(status_code=503, detail="MCP Server unavailable")

def _create_pydantic_model_from_schema(name: str, schema: Dict[str, Any]) -> Any:
    """
    Dynamically creates a Pydantic model from a JSON schema.
    Useful for creating tool argument schemas.
    """
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields = {}
    for field_name, field_info in properties.items():
        field_type = str
        # Basic type mapping - could be expanded
        if field_info.get("type") == "integer":
            field_type = int
        elif field_info.get("type") == "number":
            field_type = float
        elif field_info.get("type") == "boolean":
            field_type = bool
            
        default = ... if field_name in required else None
        fields[field_name] = (field_type, Field(default=default, description=field_info.get("description")))
    
    return create_model(f"{name}Schema", **fields)

def convert_mcp_to_langchain_tool(mcp_tool: McpToolDef, session: ClientSession) -> StructuredTool:
    """
    Converts an MCP Tool definition into a LangChain StructuredTool.
    Wraps the MCP session.call_tool method.
    """
    async def _tool_func(**kwargs) -> str:
        logger.info(f"Executing MCP Tool: {mcp_tool.name} with args: {kwargs}")
        try:
            result: CallToolResult = await session.call_tool(mcp_tool.name, arguments=kwargs)
            output = ""
            for content in result.content:
                if content.type == "text":
                    output += content.text
                elif content.type == "image":
                     output += "[Image Content]"
                elif content.type == "resource":
                     output += f"[Resource: {content.uri}]"
            logger.info("="*50)
            logger.info(f"Tool {mcp_tool.name} || Output: {output}")
            logger.info("="*50)
            return output
        except Exception as e:
            logger.error(f"Error executing tool {mcp_tool.name}: {e}")
            return f"Error executing tool: {str(e)}"

    schema = _create_pydantic_model_from_schema(mcp_tool.name, mcp_tool.inputSchema)
    
    return StructuredTool.from_function(
        func=None,
        coroutine=_tool_func,
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema=schema
    )
