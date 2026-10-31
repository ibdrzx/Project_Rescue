import streamlit as st
from agents.brief_analyst import analyze_project_brief
from agents.planning_specialist import generate_project_plan

# Page configuration
st.set_page_config(
    page_title="Project Rescue",
    page_icon="🛟",
    layout="wide"
)

st.title("🛟 Project Rescue")
st.subheader("Your AI-driven project management assistant for hackathons")

# User input text area
user_brief = st.text_area(
    "Enter your rough project brief or idea:",
    placeholder="e.g., We want to build a web-based platform for students to browse, register, and manage campus events using Python, Streamlit, and SQLite within an 8-week timeframe...",
    height=150
)

if st.button("🚀 Analyze & Generate Plan", type="primary"):
    if not user_brief.strip():
        st.warning("⚠️ Please enter a project brief first!")
    else:
        try:
            # Step 1: Brief Analyst Agent
            with st.spinner("🔍 Step 1/2: Brief Analyst is parsing your project..."):
                brief_data = analyze_project_brief(user_brief)

            st.success("✅ Brief analyzed successfully!")
            
            # Display Brief Analysis Results
            st.markdown(f"### 📋 Project Title: {brief_data.project_title}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🎯 Core Objectives:**")
                for obj in brief_data.objectives:
                    st.markdown(f"* {obj}")
                    
            with col2:
                st.markdown("**📦 Deliverables:**")
                for deliv in brief_data.deliverables:
                    st.markdown(f"* {deliv}")

            if brief_data.missing_info:
                st.markdown("**⚠️ Missing / Ambiguous Information:**")
                for info in brief_data.missing_info:
                    st.markdown(f"* {info}")

            st.markdown("---")

            # Step 2: Planning Specialist Agent
            with st.spinner("🗺️ Step 2/2: Planning Specialist is building your hackathon roadmap..."):
                plan_data = generate_project_plan(brief_data)

            st.success("✅ Roadmap generated successfully!")
            
            st.markdown(f"## 🚀 Project Roadmap: {plan_data.project_title}")
            st.markdown(f"**Total Phases:** {plan_data.total_phases}")

            # Display Milestones & Tasks inside interactive expanders
            for milestone in plan_data.milestones:
                with st.expander(f"📌 {milestone.milestone_title} (Timeline: {milestone.timeline})"):
                    for task in milestone.tasks:
                        st.markdown(f"#### 🔹 {task.task_name}")
                        st.markdown(f"> *Description:* {task.description}")
                        st.markdown(f"> **Assigned Role:** `{task.assigned_role}` &nbsp;&nbsp;|&nbsp;&nbsp; **Priority:** `{task.priority}`")
                        st.markdown("---")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
