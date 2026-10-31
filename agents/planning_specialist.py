import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Safely get API key from Streamlit secrets (Cloud) or local .env (Local)
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

class TaskItem(BaseModel):
    task_name: str = Field(description="Name of the task")
    description: str = Field(description="Brief details on what needs to be done")
    assigned_role: str = Field(description="Who should do this, e.g., Tech Lead or QA Lead")
    priority: str = Field(description="High, Medium, or Low")

class ProjectPlanSchema(BaseModel):
    milestone_name: str = Field(description="Name of the milestone, e.g., Phase 1: Setup")
    timeline: str = Field(description="Estimated time or deadline for this milestone")
    tasks: List[TaskItem] = Field(description="List of tasks belonging to this milestone")

class FullProjectPlan(BaseModel):
    milestones: List[ProjectPlanSchema] = Field(description="Complete breakdown of milestones and tasks for the hackathon")

def generate_project_plan(structured_brief_json: str) -> FullProjectPlan:
    """
    Takes the structured brief and generates an actionable milestone and task plan using Gemini.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are the Planning Specialist Agent for Project Rescue, an AI project management assistant for a two-person student hackathon team (Tech Lead and QA Lead).
    Based on the following structured project brief, create a practical, step-by-step hackathon development plan broken down into clear milestones and tasks. 
    Assign tasks appropriately between the Tech Lead and QA Lead.

    STRUCTURED BRIEF:
    {structured_brief_json}
    """

    models_to_try = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.0-flash"]
    
    last_exception = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": FullProjectPlan,
                },
            )
            return response.parsed
        except Exception as e:
            last_exception = e
            continue
            
    raise RuntimeError(f"All model attempts failed. Last error: {last_exception}")
