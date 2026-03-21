from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages
import operator

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    plan: List[str]
    completed_tasks: List[str]
    found_datasets: List[dict]
    approved_datasets: List[dict]
    findings: Annotated[list, operator.add]
    feedback_on_work: str
    final_reports: List[str]
    success_criteria: str