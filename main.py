import streamlit as st
import json
from agents.brief_analyst import analyze_project_brief
from agents.planning_specialist import generate_project_plan

# Page Configuration
st.set_page_config(
    page_title="Project Rescue",
    page_icon="🚀",
    layout="wide"
)

# App Header
st.title("🚀 Project Rescue")
st.markdown("### AI-Driven Project Management Assistant for Hackathons")
st.write("Paste your raw project brief or idea below. Our AI agents will extract the requirements and build an actionable milestone plan for your team!")

# Input Text Area
raw_brief = st.text_area(
    "📝 Project Brief / Idea Description",
    placeholder="E.g., We need to build a student event management app using Python and Streamlit...",
    height=200
)

if st.button("🚀 Analyze & Generate Plan", type="primary"):
    if not raw_brief.strip():
        st.warning("⚠️ Please enter a project brief first!")
    else:
        # Step 1: Brief Analyst Agent
        with st.status("🔍 Step 1/2: Brief Analyst is parsing your project...", expanded=True) as status:
            try:
                brief_data = analyze_project_brief(raw_brief)
                status.update(label="✅ Brief successfully analyzed!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Error in Brief Analyst: {e}")
                st.stop()

        # Display Structured Brief Results
        st.subheader("📋 Extracted Project Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**📌 Title:** {brief_data.project_title}")
            st.markdown("**🎯 Objectives:**")
            for obj in brief_data.objectives:
                st.markdown(f"- {obj}")
            st.markdown("**📦 Deliverables:**")
            for deliv in brief_data.main_deliverables:
                st.markdown(f"- {deliv}")

        with col2:
            st.markdown("**⚙️ Functional Requirements:**")
            for req in brief_data.functional_requirements:
                st.markdown(f"- {req}")
            if brief_data.constraints:
                st.markdown("**🔒 Constraints:**")
                for c in brief_data.constraints:
                    st.markdown(f"- {c}")

        if brief_data.uncertainties_or_missing_info:
            st.warning("⚠️ **Ambiguities / Missing Info to Clarify:**")
            for uncert in brief_data.uncertainties_or_missing_info:
                st.markdown(f"- {uncert}")

        st.divider()

        # Step 2: Planning Specialist Agent
        with st.status("🛠️ Step 2/2: Planning Specialist is building your hackathon roadmap...", expanded=True) as status:
            try:
                # Pass the JSON representation of the brief to the planner
                brief_json = brief_data.model_dump_json()
                plan_data = generate_project_plan(brief_json)
                status.update(label="✅ Project plan successfully generated!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Error in Planning Specialist: {e}")
                st.stop()

        # Display Project Plan Results
        st.subheader("🗺️ Hackathon Development Plan & Tasks")
        
        for milestone in plan_data.milestones:
            with st.expander(f"📌 {milestone.milestone_name} (Timeline: {milestone.timeline})", expanded=True):
                for task in milestone.tasks:
                    # Color code priority badges
                    priority_color = "red" if task.priority.lower() == "high" else "orange" if task.priority.lower() == "medium" else "blue"
                    
                    st.markdown(f"**{task.task_name}**  \n_{task.description}_")
                    st.markdown(f"👤 **Assigned To:** `{task.assigned_role}` &nbsp;&nbsp;|&nbsp;&nbsp; ⚡ **Priority:** :{priority_color}[{task.priority}]")
                    st.markdown("---")