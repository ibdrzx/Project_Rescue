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

# Define the structured output schema using Pydantic
class ProjectBriefSchema(BaseModel):
    project_title: str = Field(description="The title of the project")
    objectives: List[str] = Field(description="Main goals or objectives of the project")
    main_deliverables: List[str] = Field(description="Key deliverables expected from the project")
    functional_requirements: List[str] = Field(description="Core functional requirements")
    non_functional_requirements: Optional[List[str]] = Field(description="Performance, usability, or other non-functional requirements")
    constraints: Optional[List[str]] = Field(description="Project constraints like tech stack or limitations")
    deadlines: Optional[str] = Field(description="Project deadlines or timeframe")
    assessment_criteria: Optional[List[str]] = Field(description="Important grading or evaluation criteria")
    uncertainties_or_missing_info: List[str] = Field(description="Any ambiguities or missing details the user should clarify")

def analyze_project_brief(brief_text: str) -> ProjectBriefSchema:
    """
    Analyzes an unstructured project brief text using Gemini and returns a structured Pydantic schema.
    Includes robust fallback models for reliability.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are the Brief Analyst Agent for Project Rescue, an AI project management assistant for students.
    Analyze the following project brief carefully. Extract all structured details. 
    If anything important is missing or ambiguous, list it clearly in the uncertainties_or_missing_info field. Do not invent fake requirements.

    PROJECT BRIEF:
    {brief_text}
    """

    # Updated list of current stable models to try in order
    models_to_try = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.0-flash"]
    
    last_exception = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProjectBriefSchema,
                },
            )
            return response.parsed
        except Exception as e:
            last_exception = e
            continue  # Try the next model
            
    # If all models failed, raise the final exception
    raise RuntimeError(f"All model attempts failed. Last error: {last_exception}")
