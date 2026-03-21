import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import ResearchState
from tools.code_tools import run_python_code
from tools.playwright_tools import playwright_tools
from typing import Dict, Any
from dotenv import load_dotenv

class Engineer:
    def __init__(self):
        load_dotenv(override=True)
        self.llm_with_tools = None
        self.tools = []

    async def setup(self, existing_browser, existing_playwright):
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        p_tools, _, _ = await playwright_tools(browser=existing_browser, playwright=existing_playwright)
        self.tools = p_tools + [run_python_code]
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self

    def work(self, state: ResearchState) -> Dict[str, Any]:
        all_findings = state.get("findings", [])

        os.makedirs("research_sandbox", exist_ok=True)
        sandbox = os.path.join(os.getcwd(), "research_sandbox")
        findings_str = "\n".join([f"- {f['title']} | URL: {f['url']}" for f in all_findings])

        system_message = f"""You are a Senior Data Engineer. Download findings to {sandbox}:
        {findings_str if all_findings else "None"}

        CRITICAL DOWNLOAD RULES:
        1. GITHUB: Always use 'run_python_code' to run `git clone`. Do NOT use the browser for GitHub.
        2. ARXIV/MENDELEY: Use 'navigate_browser' to find the PDF link, then use 'run_python_code' to download it.
        3. BYPASS ABORTS: Even if the Scout reported a 'net::ERR_ABORTED' for a URL, you MUST attempt to download it using 'run_python_code' (requests or git) anyway.
        4. VERIFY: You must call 'run_python_code' to list the files in the sandbox to prove success."""

        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        response = self.llm_with_tools.invoke([SystemMessage(content=system_message)] + filtered_messages)
        return {"messages": [response]}