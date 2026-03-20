import gradio as gr
import asyncio
from graph import create_research_graph
from langchain_core.messages import HumanMessage

async def run_research(topic):
    graph = await create_research_graph()
    
    inputs = {
        "messages": [HumanMessage(content=topic)],
        "topic": topic,
        "plan": [],
        "success_criteria": []
    }
    
    final_output = ""
    async for event in graph.astream(inputs, stream_mode="values"):
        if "messages" in event:
            last_message = event["messages"][-1]
            if hasattr(last_message, 'content'):
                final_output += f"\n\n--- {type(last_message).__name__} ---\n{last_message.content}"
    
    return final_output

def gradio_wrapper(topic):
    return asyncio.run(run_research(topic))

demo = gr.Interface(
    fn=gradio_wrapper,
    inputs=gr.Textbox(label="Research Topic", placeholder="Enter a topic (e.g., 'Wolof speech datasets')"),
    outputs=gr.Markdown(label="Research Log"),
    title="AI Research Lab",
    description="Multi-agent system using LangGraph, ArXiv, and Playwright."
)

if __name__ == "__main__":
    demo.launch()