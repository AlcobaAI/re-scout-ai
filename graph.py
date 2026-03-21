from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from state import ResearchState
from agents.planner import Planner

def handle_tool_error(error) -> str:
    """Helper to catch browser errors and tell the Scout to try something else."""
    return f"The tool encountered an error: {str(error)}. Please try a different URL or a different search strategy."

async def create_research_graph(scout_agent, engineer_agent):
    planner_agent = Planner()
    await planner_agent.setup()

    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_agent.plan)
    builder.add_node("scout", scout_agent.scout)
    builder.add_node("engineer", engineer_agent.work)
    planner_tool_node = ToolNode(
        planner_agent.tools, 
        handle_tool_errors=handle_tool_error
    )
    scout_tool_node = ToolNode(
        scout_agent.tools, 
        handle_tool_errors=handle_tool_error
    )
    engineer_tool_node = ToolNode(
        engineer_agent.tools, 
        handle_tool_errors=handle_tool_error
    )
    
    builder.add_node("planner_tools", planner_tool_node)
    builder.add_node("scout_tools", scout_tool_node)
    builder.add_node("engineer_tools", engineer_tool_node)

    builder.add_edge(START, "planner")
    
    builder.add_edge("planner_tools", "planner")
    builder.add_conditional_edges(
        "planner", 
        tools_condition, 
        {
            "tools": "planner_tools", 
            "__end__": "scout"
        }
    )

    builder.add_edge("scout_tools", "scout")
    builder.add_conditional_edges(
        "scout", 
        tools_condition, 
        {
            "tools": "scout_tools", 
            "__end__": "engineer"
        }
    )

    builder.add_edge("engineer_tools", "engineer")
    builder.add_conditional_edges(
        "engineer", 
        tools_condition, 
        {
            "tools": "engineer_tools", 
            "__end__": END
        }
    )

    return builder.compile()