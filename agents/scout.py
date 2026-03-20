from dotenv import load_dotenv
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import ResearchState
from tools.search_tools import search_tools
from tools.playwright_tools import playwright_tools

class Scout:
    def __init__(self):
        load_dotenv(override=True)
        self.llm_with_tools = None
        self.tools = []
        self.browser = None
        self.playwright = None


    async def setup(self):
        llm = ChatOpenAI(model="gpt-4o-mini")
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await search_tools()
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self

    def scout(self, state: ResearchState) -> Dict[str, Any]:
        system_message = """You are a research assistant tasked with finding datasets for a research project.
        Use the tools at your disposal to search for relevant datasets, evaluate their quality, and compile a report of your findings."""

        if state.get("feedback_on_work"):
            system_message += f"""
        Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
        Here is the feedback on why this was rejected:
        {state["feedback_on_work"]}
        With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""
            
        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        return {
            "messages": [response],
        }