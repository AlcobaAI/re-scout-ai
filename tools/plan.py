from typing import List
from pydantic import BaseModel, Field

class SetPlan(BaseModel):
    """Sets the formal research plan, refined topic, and success criteria."""
    topic: str = Field(description="A concise summary of the research goal.")
    steps: List[str] = Field(description="Step-by-step instructions for the Scout.")
    success_criteria: List[str] = Field(description="Measurable conditions for completion.")