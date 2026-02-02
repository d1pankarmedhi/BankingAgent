import os
import argparse
from mcp_client.agent_graph import create_agent_graph

def main():
    parser = argparse.ArgumentParser(description="Visualize the LangGraph agent graph.")
    parser.add_argument("--output", default="agent_graph.png", help="Output filename (default: agent_graph.png)")
    args = parser.parse_args()

    # Mock LLM for visualization 
    class MockLLM:
        def bind_tools(self, tools): return self
        def ainvoke(self, messages): pass

    graph = create_agent_graph(tools=[], llm=MockLLM())
    
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        
        with open(args.output, "wb") as f:
            f.write(png_data)
        
        print(f"Successfully saved graph visualization to {args.output}")
    except Exception as e:
        print(f"Error generating graph: {e}")
        print("Note: This feature requires 'pygraphviz', 'pydot', or 'graphviz' installed, ")
        print("or use graph.get_graph().draw_mermaid() to get the mermaid syntax.")

if __name__ == "__main__":
    main()
