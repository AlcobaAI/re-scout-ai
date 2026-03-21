import os
from langchain_experimental.tools import PythonREPLTool
from langchain_core.tools import tool

repl = PythonREPLTool()

@tool
def run_python_code(code: str):
    """
    Executes Python code locally to download datasets, clone repos, or process files.
    All file operations should target the 'research_sandbox' directory.
    Input should be valid Python code string.
    """

    sandbox_path = os.path.join(os.getcwd(), "research_sandbox")
    os.makedirs(sandbox_path, exist_ok=True)
    
    # This helps the LLM not have to guess the absolute path every time
    env_context = f"import os\nSANDBOX='{sandbox_path.replace('\\', '/')}'\nos.makedirs(SANDBOX, exist_ok=True)\n"
    full_code = env_context + code
    
    return repl.run(full_code)