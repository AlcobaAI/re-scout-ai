from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

async def playwright_tools(browser=None, playwright=None):
    """
    Initializes or reuses Playwright instances to provide LangChain tools.
    """
    if playwright is None:
        playwright = await async_playwright().start()
    
    if browser is None:
        browser = await playwright.chromium.launch(headless=True)
    
    browser_toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    tools = browser_toolkit.get_tools()
    
    return tools, browser, playwright