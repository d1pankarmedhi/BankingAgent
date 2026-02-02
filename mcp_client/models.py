from typing import List, Dict, Optional, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    customer_id: str = "C001"  # Default customer ID

class ChatResponse(BaseModel):
    response: str

# Define Agent State
class AgentState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    plan: Optional[str] = None
    steps_taken: List[str] = Field(default_factory=list)
    reflections: List[str] = Field(default_factory=list)
