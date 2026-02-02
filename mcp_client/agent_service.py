import os
import logging
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from mcp import ClientSession
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from mcp_client.models import ChatRequest
from mcp_client.mcp_utils import get_mcp_session, convert_mcp_to_langchain_tool
from mcp_client.agent_graph import create_agent_graph

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce noise from external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

app = FastAPI(title="Banking Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: ChatRequest, session: ClientSession = Depends(get_mcp_session)):
    async def event_generator():
        try:
            # Discover Tools
            logger.info("Discovering tools...")
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            
            # Convert to LangChain Tools
            lc_tools = [convert_mcp_to_langchain_tool(t, session) for t in mcp_tools]

            # Create Agent
            agent = create_agent_graph(lc_tools)

            # Prepare Input
            system_prompt = f"""You are a helpful Banking Agent. Use a Plan-Execute-Reflect cycle to resolve queries.
            
            ### RULES & IDENTITY
            - **Current Customer:** {request.customer_id}
            - **Available Tools:** Account info, balance, stocks, commodities.
            - **Formatting:** Use Markdown tables for data. Be professional and concise.
            - **IDs:** Never expose internal raw IDs to the user.
            - **Consistency:** Always use the provided customer_id for tool calls.
            """
            
            messages = [SystemMessage(content=system_prompt)]
            for msg in request.history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content")))
            
            messages.append(HumanMessage(content=request.message))

            # Execute Agent with Streaming
            logger.info("Streaming agent execution...")
            steps = []
            final_response = ""
            
            async for chunk in agent.astream({"messages": messages}, stream_mode="updates"):
                for node, data in chunk.items():
                    logger.info(f"Node complete: {node}")
                    
                    if node == "planner":
                        plan = data.get("plan", "")
                        status = "Created execution plan"
                        yield json.dumps({"type": "status", "content": status}) + "\n"
                        steps.append({"title": "Planning", "content": plan, "type": "plan"})
                    
                    elif node == "agent":
                        msg = data.get("messages", [])[-1]
                        if msg.tool_calls:
                            tool = msg.tool_calls[0]['name']
                            status = f"Decided to call {tool}"
                            yield json.dumps({"type": "status", "content": status}) + "\n"
                        else:
                            final_response = msg.content
                    
                    elif node == "tools":
                        status = "Executed banking tool"
                        yield json.dumps({"type": "status", "content": status}) + "\n"
                    
                    elif node == "reflector":
                        ref = data.get("reflections", [""])[0]
                        step = data.get("steps_taken", [""])[0]
                        status = f"Reflecting: {step}"
                        yield json.dumps({"type": "status", "content": status}) + "\n"
                        steps.append({"title": "Reflection", "content": f"{step}\n\n{ref}", "type": "reflection"})

            # Final response
            yield json.dumps({
                "type": "final", 
                "content": final_response,
                "steps": steps
            }) + "\n"

        except Exception as e:
            logger.exception("Error in streaming response")
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
