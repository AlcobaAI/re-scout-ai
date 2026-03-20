import gradio as gr
import asyncio
import sqlite3
import pandas as pd
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
                    final_output += f"\n\n--- Update ---\n{last_message.content}"
        return final_output
    except Exception as e:
        return f"Error during research: {str(e)}"
    finally:
        print("Cleaning up Playwright...")
        scout_inst.cleanup()

def gradio_wrapper(topic):
    return asyncio.run(run_research(topic))

def get_db_summary():
    try:
        conn = sqlite3.connect("research_archive.db")
        datasets_df = pd.read_sql_query("SELECT * FROM datasets ORDER BY id DESC LIMIT 50", conn)
        papers_df = pd.read_sql_query("SELECT * FROM papers ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return datasets_df, papers_df
    except Exception as e:
        error_df = pd.DataFrame({"Status": [f"Error: {str(e)}"]})
        return error_df, pd.DataFrame()

with gr.Blocks(title="AI Research Lab v2.0") as demo:
    gr.Markdown("# 🧪 AI Research Lab")
    
    with gr.Tabs():
        with gr.TabItem("Research Lab"):
            gr.Markdown("Enter a topic to start the automated multi-agent research process.")
            with gr.Row():
                topic_input = gr.Textbox(
                    label="Research Topic", 
                    placeholder="e.g., Arabic Dialect Identification datasets",
                    lines=1
                )
            submit_btn = gr.Button("Start Research", variant="primary")
            research_log = gr.Markdown(label="Research Log")
            
            submit_btn.click(
                fn=gradio_wrapper,
                inputs=topic_input,
                outputs=research_log
            )

        with gr.TabItem("Database Explorer"):
            gr.Markdown("### 🗄️ Research Archive Explorer")
            refresh_btn = gr.Button("Refresh View", variant="secondary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📊 Saved Datasets")
                    dataset_table = gr.Dataframe(interactive=False)
                with gr.Column():
                    gr.Markdown("#### 📜 Saved Academic Papers")
                    paper_table = gr.Dataframe(interactive=False)
            
            refresh_btn.click(
                fn=get_db_summary, 
                inputs=None, 
                outputs=[dataset_table, paper_table]
            )
            demo.load(fn=get_db_summary, outputs=[dataset_table, paper_table])

if __name__ == "__main__":
    demo.launch()