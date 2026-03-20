import gradio as gr
import asyncio
from database import setup_db
from graph import create_research_graph
from agents.scout import Scout
from langchain_core.messages import HumanMessage

async def run_research(topic):
    setup_db()
    
    scout_inst = Scout()
    await scout_inst.setup()
    
    graph = await create_research_graph(scout_inst)
    
    inputs = {
        "messages": [HumanMessage(content=topic)],
        "topic": topic,
        "plan": [],
        "success_criteria": []
    }
    
    final_output = ""
    try:
        async for event in graph.astream(inputs, stream_mode="values"):
            if "messages" in event:
                last_message = event["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    node_name = "Agent"
                    final_output += f"\n\n--- Update ---\n{last_message.content}"
        
        return final_output

    except Exception as e:
        return f"Error during research: {str(e)}"
    
    finally:
        print("🧹 Cleaning up Playwright...")
        scout_inst.cleanup()

def gradio_wrapper(topic):
    return asyncio.run(run_research(topic))

demo = gr.Interface(
    fn=gradio_wrapper,
    inputs=gr.Textbox(
        label="Research Topic", 
        placeholder="Enter a topic (e.g., 'Arabic speech dialect identification')"
    ),
    outputs=gr.Markdown(label="Research Log"),
    title="AI Research Lab",
    description="Automated multi-agent system. The Planner will draft the criteria and the Scout will find the data."
)

if __name__ == "__main__":
    demo.launch()