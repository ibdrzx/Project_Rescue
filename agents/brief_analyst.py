import os
import time
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

class ProjectBriefSchema(BaseModel):
    project_title: str = Field(description="The name or title of the project.")
    objectives: List[str] = Field(description="Core goals and objectives of the project.")
    deliverables: List[str] = Field(description="Expected outputs or features to be built.")
    missing_info: Optional[List[str]] = Field(default=[], description="Any ambiguous or missing information in the brief.")

# Ensure Pydantic fully resolves the model schema
ProjectBriefSchema.model_rebuild()

def analyze_project_brief(brief_text: str) -> ProjectBriefSchema:
    """
    Analyzes the raw project brief using Gemini with automatic 503 retry handling.
    """
    prompt = f"""
    Analyze the following project brief and extract the structured details.
    
    Project Brief:
    {brief_text}
    """
    
    max_retries = 3
    delay = 2  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProjectBriefSchema,
                },
            )
            return ProjectBriefSchema.model_validate_json(response.text)
            
        except Exception as e:
            # Catch server-side 503 high demand spikes and retry automatically
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                raise e
