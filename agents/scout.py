import asyncio
import uuid

from dotenv import load_dotenv
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import ResearchState
import state
from tools.search_tools import search_tools
from tools.playwright_tools import playwright_tools
from tools.database_tools import save_paper_found, save_dataset_found

class Scout:
    def __init__(self):
        load_dotenv(override=True)
        self.llm_with_tools = None
        self.tools = []
        self.browser = None
        self.playwright = None
        self.scout_id = str(uuid.uuid4())


    async def setup(self):
        llm = ChatOpenAI(model="gpt-4o-mini")
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await search_tools()
        self.tools.append(save_paper_found)
        self.tools.append(save_dataset_found)
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self

    def scout(self, state: ResearchState) -> Dict[str, Any]:
        system_message = f"""You are an expert Research Scout. Your goal is to execute the following research plan:
        Topic: {state.get('topic')}
        Steps: {state.get('plan')}
        Success Criteria: {state.get('success_criteria')}

        OPERATIONAL REQUIREMENTS:
        1. When you find an academic paper on ArXiv, you MUST call 'save_paper_found'.
        2. When you find a dataset (on GitHub, HuggingFace, etc.), you MUST call 'save_dataset_found'.
        3. IMPORTANT: If a dataset was found within or because of a specific paper, provide that paper's 'arxiv_id' to the 'save_dataset_found' tool to link them in the database.
        4. Do not guess links. Use your browser tools to verify a URL exists before saving it."""

        if state.get("feedback_on_work"):
            system_message += f"""
        
        CRITICAL FEEDBACK ON PREVIOUS ATTEMPT:
        {state["feedback_on_work"]}
        Please adjust your strategy to address this feedback specifically."""
                        
        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        findings = state.get("findings", [])

        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                if tool_call["name"] == "save_dataset_found":
                    args = tool_call["args"]
                    finding_entry = {
                        "title": args.get("name") or args.get("title"),
                        "url": args.get("url"),
                        "platform": "GitHub" if "github" in args.get("url", "").lower() else "HuggingFace" if "huggingface" in args.get("url", "").lower() else "Direct",
                        "description": args.get("description", "")
                    }
                    if finding_entry not in findings:
                        findings.append(finding_entry)

        return {
            "messages": [response],
            "findings": findings
        }

    def cleanup(self):
        """Standardized cleanup logic from Sidekick pattern."""
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                asyncio.run(self.browser.close())
                if self.playwright:
                    asyncio.run(self.playwright.stop())
            print("✅ Browser resources cleaned up.")