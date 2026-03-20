from urllib import response

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

        system_message = f"""You are an experienced Research Lead specializing in Dataset Sourcing. 
            Your goal is to refine the topic: '{current_topic}' into a data-acquisition plan.

            ### STRATEGY CONSTRAINTS:
            1. DATA-CENTRIC ONLY: The plan must focus ONLY on identifying, locating, and verifying datasets, papers, and repositories. 
               - DO NOT include training models, building frameworks, or analysis.
               - DO include: ArXiv searches, GitHub repository lookups, and dataset portal verification.

            2. SUCCESS CRITERIA: You MUST define at least 3-5 quantitative success criteria in 'SetPlan'.
               - Examples: "Identify 5 relevant ArXiv papers from 2024-2025", "Locate 2 GitHub repos with downloadable .wav or .txt data".

            ### WORKFLOW:
            1. IF the topic is broad: Use 'search_arxiv' or 'google_search' to see what's available.
            2. IF you know what to look for: Use 'SetPlan' to formalize the Research Topic, Steps (data-focused), and Success Criteria (data-focused).
            3. ONCE 'SetPlan' is called: Summarize the data-sourcing strategy and signal the Scout to begin.

            Do not guess. Verify that datasets likely exist before finalizing the plan."""
        
        if state.get("feedback_on_work"):
            system_message += f"\n\nREVISION REQUIRED: {state['feedback_on_work']}"
            
        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        update = {"messages": [response]}
    
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                if tool_call["name"] == "SetPlan":
                    args = tool_call["args"]
                    update["plan"] = args.get("steps", [])
                    update["success_criteria"] = args.get("success_criteria", [])
                    update["topic"] = args.get("topic", state.get("topic"))

        return update