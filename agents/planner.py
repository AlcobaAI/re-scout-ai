from dotenv import load_dotenv
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from state import ResearchState
from tools.search_tools import search_tools

class SetPlan(BaseModel):
    """Sets the formal research plan, refined topic, and success criteria."""
    topic: str = Field(description="A concise summary of the research goal.")
    steps: List[str] = Field(description="Step-by-step instructions for the Scout.")
    success_criteria: List[str] = Field(description="Measurable conditions for completion.")

class Planner:
    def __init__(self):
        load_dotenv()
        self.llm_with_tools = None
        self.tools = []

    async def setup(self):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # Low temp for planning
        
        s_tools = await search_tools()
        self.tools = s_tools + [SetPlan] 
        
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self
    
    def plan(self, state: ResearchState) -> Dict[str, Any]:
        current_topic = state.get("topic", "No topic provided")
        
        system_message = f"""You are an experienced Research Lead. 
        Your goal is to refine the topic: '{current_topic}' into a concrete execution plan.

        You MUST use the 'SetPlan' tool to save your findings. 
        Break the research down into actionable steps for the Scout agent.
        Define clear success criteria (e.g., 'Find 3 GitHub repos', 'Locate CSV files')."""
        
        if state.get("feedback_on_work"):
            system_message += f"\n\nREVISION REQUIRED: {state['feedback_on_work']}"
            
        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        return {
            "messages": [response],
        }