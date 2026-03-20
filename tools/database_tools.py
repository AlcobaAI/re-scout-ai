from langchain_core.tools import tool
from database import save_paper, save_dataset, link_paper_to_dataset

@tool
def save_paper_found(title: str, arxiv_id: str, summary: str, pdf_link: str, authors: str) -> str:
    """
    Saves an academic paper and its summary to the local research database.
    Use this for every relevant paper identified during research.
    Returns the database ID of the paper for linking purposes.
    """
    try:
        paper_id = save_paper(title, arxiv_id, summary, pdf_link, authors)
        return f"Successfully saved paper '{title}' (ID: {paper_id})."
    except Exception as e:
        return f"Error saving paper: {str(e)}"

@tool
def save_dataset_found(name: str, url: str, task: str, languages: str, paper_arxiv_id: str = None) -> str:
    """
    Saves a dataset to the database. 
    If 'paper_arxiv_id' is provided, it automatically links this dataset 
    to that specific paper in the research archive.
    """
    try:
        # 1. Save the dataset and get its ID
        dataset_id = save_dataset(name, url, task, languages)
        result_msg = f"Successfully saved dataset '{name}' (ID: {dataset_id})."

        # 2. Link to paper if an ArXiv ID was provided
        if paper_arxiv_id:
            paper_id = save_paper("", paper_arxiv_id, "", "", "") 
            linked = link_paper_to_dataset(paper_id, dataset_id)
            if linked:
                result_msg += f" Linked to paper {paper_arxiv_id}."
        
        return result_msg
    except Exception as e:
        return f"Error in database operation: {str(e)}"