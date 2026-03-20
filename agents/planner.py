from dotenv import load_dotenv
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from state import ResearchState
from tools.plan import SetPlan
from tools.search_tools import search_tools

class Planner:
    def __init__(self):
        load_dotenv(override=True)
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
        Your first priority is to understand the feasibility of the user's request.

        1. IF the topic is broad or unfamiliar: Use 'search_arxiv' or 'google_search' to find preliminary context.
        2. IF you have enough information: Use the 'SetPlan' tool to formalize the Research Topic, Steps, and Success Criteria.
        3. ONCE 'SetPlan' is called and you see the result: Summarize the strategy and signal that the Scout should begin.

        Your goal is to refine the topic: '{current_topic}' into a concrete execution plan.

        Do not guess. If you aren't sure if datasets exist, search first."""
        
        if state.get("feedback_on_work"):
            system_message += f"\n\nREVISION REQUIRED: {state['feedback_on_work']}"
            
        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        return {
            "messages": [response],
        }