import os
import streamlit as st
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Safely get API key from Streamlit secrets (Cloud) or local .env (Local)
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

class Task(BaseModel):
    task_name: str = Field(description="Name of the task.")
    description: str = Field(description="Brief details on how to implement this task.")
    assigned_role: str = Field(description="Recommended role (e.g., Tech Lead, UI/UX, QA).")
    priority: str = Field(description="Priority level: High, Medium, or Low.")

class Milestone(BaseModel):
    milestone_title: str = Field(description="Title of the milestone.")
    timeline: str = Field(description="Estimated timeframe or deadline.")
    tasks: List[Task] = Field(description="List of tasks required to complete this milestone.")

class ProjectPlanSchema(BaseModel):
    project_title: str = Field(description="Title of the project.")
    total_phases: int = Field(description="Total number of implementation phases.")
    milestones: List[Milestone] = Field(description="Structured milestones and tasks for the hackathon.")

# Ensure Pydantic fully resolves nested model schemas
ProjectPlanSchema.model_rebuild()

def generate_project_plan(brief_data) -> ProjectPlanSchema:
    """
    Generates a structured hackathon project plan using Gemini based on the analyzed brief.
    """
    prompt = f"""
    Create a detailed hackathon project plan and milestone breakdown based on this project brief data:
    {brief_data}
    """
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ProjectPlanSchema,
        },
    )
    
    return ProjectPlanSchema.model_validate_json(response.text)
