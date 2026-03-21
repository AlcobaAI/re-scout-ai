import asyncio
from dotenv import load_dotenv
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import ResearchState
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

    async def setup(self):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # Initialize shared playwright instance
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await search_tools()
        self.tools.extend([save_paper_found, save_dataset_found])
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self

    def scout(self, state: ResearchState) -> Dict[str, Any]:
        system_message = f"""You are an expert Research Scout. 
        Topic: {state.get('topic')}
        
        OPERATIONAL REQUIREMENTS:
        1. If 'navigate_browser' returns ERR_ABORTED, do not give up. If the URL looks valid (especially GitHub), call 'save_dataset_found' anyway so the Engineer can try to clone it.
        2. Verify as much as possible, but prioritize passing potential data sources to the Engineer."""

        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        response = self.llm_with_tools.invoke([SystemMessage(content=system_message)] + filtered_messages)

        new_findings = []
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                if tool_call["name"] == "save_dataset_found":
                    args = tool_call["args"]
                    url = args.get("url", "")
                    entry = {
                        "title": args.get("name") or args.get("title"),
                        "url": url,
                        "platform": "GitHub" if "github" in url.lower() else "HuggingFace" if "huggingface" in url.lower() else "Direct"
                    }
                    if entry not in state.get("findings", []):
                        new_findings.append(entry)

        return {"messages": [response], "findings": new_findings}

    def cleanup(self):
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
            except RuntimeError:
                asyncio.run(self.browser.close())