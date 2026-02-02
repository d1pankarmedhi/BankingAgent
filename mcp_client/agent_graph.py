from typing import List, Literal
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from mcp_client.llm_config import get_llm
from mcp_client.models import AgentState

def create_agent_graph(tools: List[StructuredTool], llm=None):
    """
    Constructs the LangGraph StateGraph for a robust Banking agent.
    Incorporates Planning, Execution, and Reflection nodes.
    """
    # Get LLM from configuration if not provided
    if llm is None:
        llm = get_llm(temperature=0.8)
    
    llm_with_tools = llm.bind_tools(tools)

    async def planner_node(state: AgentState):
        """Creates an initial plan based on the user request."""
        messages = state.messages
        planner_prompt = """Based on the user's request and history, create a concise step-by-step plan to resolve the query. Identify specific tools likely needed."""
        
        plan_messages = [SystemMessage(content=planner_prompt)] + messages
        response = await llm.ainvoke(plan_messages)
        return {"plan": response.content}

    async def agent_node(state: AgentState):
        """Decides the next action (tool call) based on the plan and history."""
        messages = state.messages
        plan = state.plan
        steps = "\n".join(state.steps_taken)
        reflections = "\n".join(state.reflections)

        agent_prompt = f"""Current Plan: {plan}
        Steps Taken: {steps}
        Recent Reflections: {reflections}
        
        Decide the next action. If the plan is fulfilled, provide the final answer."""
        
        # Inject context into messages for the LLM
        context_msg = SystemMessage(content=agent_prompt)
        response = await llm_with_tools.ainvoke([context_msg] + messages)
        return {"messages": [response]}

    async def reflector_node(state: AgentState):
        """Analyzes tool output and updates the state."""
        messages = state.messages
        
        reflection_prompt = """Analyze the recent tool output. Determine if it satisfies the sub-query/plan step and if further tools are needed. Provide a brief reflection."""
        
        # We look at the messages since the last AI message
        relevant_messages = []
        for msg in reversed(messages):
            relevant_messages.append(msg)
            if isinstance(msg, AIMessage) and msg.tool_calls:
                break
        
        response = await llm.ainvoke([SystemMessage(content=reflection_prompt)] + list(reversed(relevant_messages)))
        
        # Record the step taken (the tool call)
        last_ai_msg = [m for m in messages if isinstance(m, AIMessage) and m.tool_calls][-1]
        tool_call = last_ai_msg.tool_calls[0]['name']
        
        return {
            "reflections": [response.content],
            "steps_taken": [f"Called tool: {tool_call}"]
        }

    def should_continue(state: AgentState) -> Literal["tools", "reflector", "__end__"]:
        messages = state.messages
        last_message = messages[-1]
        
        if last_message.tool_calls:
            return "tools"
        
        # If it's a ToolMessage (output of tools), we reflect
        if hasattr(last_message, "type") and last_message.type == "tool":
            return "reflector"
            
        return "__end__"

    def after_reflection(state: AgentState) -> Literal["agent", "__end__"]:
        # Decide if we need more steps or if we can end
        return "agent"

    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("reflector", reflector_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    
    workflow.add_edge("tools", "reflector")
    workflow.add_conditional_edges(
        "reflector",
        after_reflection,
    )

    return workflow.compile()
