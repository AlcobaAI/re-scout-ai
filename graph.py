# graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from agents import planner
from state import ResearchState
from agents.planner import Planner
from agents.scout import Scout

def handle_tool_error(error) -> str:
    """Helper to catch browser errors and tell the Scout to try something else."""
    return f"The tool encountered an error: {str(error)}. Please try a different URL or a different search strategy."

async def create_research_graph():
    planner_agent = Planner()
    await planner_agent.setup()
    
    scout_agent = Scout()
    await scout_agent.setup()

    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_agent.plan)
    builder.add_node("scout", scout_agent.scout)

    planner_tool_node = ToolNode(
    planner_agent.tools, 
    handle_tool_errors=handle_tool_error
)
    scout_tool_node = ToolNode(
    scout_agent.tools, 
    handle_tool_errors=handle_tool_error
)
    
    builder.add_node("planner_tools", planner_tool_node)
    builder.add_node("scout_tools", scout_tool_node)

    builder.add_edge(START, "planner")
    
    builder.add_conditional_edges(
        "planner", 
        tools_condition, 
        {
            "tools": "planner_tools", 
            END: "scout"
        }
    )
    builder.add_edge("planner_tools", "planner")

    builder.add_conditional_edges(
        "scout", 
        tools_condition, 
        {
            "tools": "scout_tools", 
            END: END
        }
    )
    builder.add_edge("scout_tools", "scout")

    return builder.compile()