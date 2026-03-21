from dotenv import load_dotenv
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import ResearchState
from tools.code_tools import run_python_code
from tools.playwright_tools import playwright_tools

class Engineer:
    def __init__(self):
        load_dotenv(override=True)
        self.llm_with_tools = None

    async def setup(self, existing_browser, existing_playwright):
        llm = ChatOpenAI(model="gpt-4o", temperature=0) 
        self.tools, _, _ = await playwright_tools(
            browser=existing_browser, 
            playwright=existing_playwright
        )
        self.tools.append(run_python_code)
        self.llm_with_tools = llm.bind_tools(self.tools)
        return self

    def work(self, state: ResearchState) -> Dict[str, Any]:
        current_topic = state.get("topic", "No topic provided")
        findings = state.get("findings", [])

        system_message = f"""You are a Senior Data Engineer. 
        Your goal is to download the datasets identified by a researcher for the topic: '{current_topic}'.

        ### TARGET DIRECTORY:
        All files MUST be downloaded into the directory stored in the variable `SANDBOX`.

        ### OPERATIONAL PROTOCOL:
        1. REVIEW findings: {findings}
        2. For each dataset, determine the appropriate download method based on the source (Hugging Face, GitHub, direct URL).
        3. If you do not have a direct URL for a dataset, attempt to find one using the information provided (e.g., paper links, repository names), and the tools available (Playwright).
        4. CHOOSE METHOD:
           - Hugging Face: Use 'from huggingface_hub import snapshot_download'.
           - GitHub: Use 'import subprocess; subprocess.run(["git", "clone", ...])'.
           - Direct URLs: Use 'import requests'.
        5. EXECUTE: Use 'run_python_code' to perform the download.
        6. VERIFY: After downloading, list the files in `SANDBOX` to confirm success.

        If a URL is missing or broken, report it and move to the next.
        Do not delete existing files in the sandbox unless necessary for a clean download."""

        filtered_messages = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        full_messages = [SystemMessage(content=system_message)] + filtered_messages

        response = self.llm_with_tools.invoke(full_messages)

        return {"messages": [response]}