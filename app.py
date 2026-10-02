import os
import sys

# 1. Root directory ko Python path me add karein (sys/os import hone ke foran baad)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import json
import uuid
import streamlit as st

# 2. Local Agents Import (Path fix hone ke baad)
try:
    from src.agents.planner import ResearchPlanner
    from src.agents.evidence_analyst import EvidenceAnalyst
    from src.agents.quality_control import QualityControlAgent
    from src.agents.report_generator import ReportGenerator
except Exception as e:
    st.error(f"Failed to import agents from src folder: {e}")

# 3. Page Configuration
st.set_page_config(
    page_title="MarketMind AI — Autonomous Research Agent",
    page_icon="🧠",
    layout="wide"
)

# 4. Session State Setup
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""
if "research_results" not in st.session_state:
    st.session_state["research_results"] = None

# 5. API Key Input Screen (Center Screen Gate)
if not st.session_state["openai_api_key"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.title("🧠 MarketMind AI")
        st.subheader("Autonomous Business Research Agent")
        st.write("Please enter your OpenAI API key to access the research platform.")
        
        api_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if st.button("Enter Platform", use_container_width=True):
            if api_input.strip().startswith("sk-"):
                st.session_state["openai_api_key"] = api_input.strip()
                st.rerun()
            else:
                st.error("Please enter a valid OpenAI API Key starting with 'sk-'")
    st.stop()

# ------------------------------------------------------------------
# 6. MAIN APPLICATION INTERFACE
# ------------------------------------------------------------------
api_key = st.session_state["openai_api_key"]

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Agent Controls")
    st.success("API Key Active ✅")
    
    if st.button("Change API Key"):
        st.session_state["openai_api_key"] = ""
        st.session_state["research_results"] = None
        st.rerun()
        
    st.divider()
    max_iterations = st.slider("Max Research Iterations", min_value=1, max_value=10, value=5)
    run_cost_limit = st.number_input("Cost Limit ($)", min_value=1.0, max_value=50.0, value=10.0)
    
    st.caption("Verity Strategy Partners — Market Intelligence Practice")

# Header Section
st.title("🧠 MarketMind AI — Business Intelligence Brief Generator")
st.caption("Decomposed, Provenance-Backed Market Research System")

# Research Topic Input
topic_input = st.text_area(
    "Enter Research Topic / Client Brief Request:",
    placeholder="e.g., Who competes in the AI Customer Support market, how are they differentiated, and where is the market heading?",
    height=100
)

col_run, col_clear = st.columns([1, 4])
with col_run:
    run_button = st.button("🚀 Start Autonomous Research", type="primary", use_container_width=True)

if run_button:
    if not topic_input.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state["research_results"] = None
        
        with st.status("Executing MarketMind Agentic Pipeline...", expanded=True) as status:
            try:
                # Step 1: Question Decomposition (Planner)
                st.write("📋 **Step 1/4:** Decomposing scope into research questions...")
                planner = ResearchPlanner(api_key=api_key)
                plan = planner.plan(topic_input)
                st.write(f"✓ Created research plan with {len(plan.get('questions', []))} questions.")

                # Step 2: Evidence Collection & Extraction
                st.write("🔎 **Step 2/4:** Collecting sources & extracting typed evidence...")
                analyst = EvidenceAnalyst(api_key=api_key)
                analysis = analyst.analyze(topic_input, research_plan=plan)
                st.write("✓ Evidence extracted and epistemically categorized.")

                # Step 3: Quality Control Pass
                st.write("🛡️ **Step 3/4:** Performing QC check for unsupported claims & coverage...")
                qc_agent = QualityControlAgent(api_key=api_key)
                qc_results = qc_agent.review(report_draft=str(analysis), research_plan=plan)
                st.write("✓ Quality Control evaluation complete.")

                # Step 4: Final Synthesis & Brief Generation
                st.write("📝 **Step 4/4:** Synthesizing Markdown Market Intelligence Brief...")
                generator = ReportGenerator(api_key=api_key)
                final_brief = generator.generate(
                    topic=topic_input,
                    analysis_data=analysis,
                    qc_feedback=qc_results
                )

                st.session_state["research_results"] = {
                    "topic": topic_input,
                    "plan": plan,
                    "analysis": analysis,
                    "qc": qc_results,
                    "brief": final_brief
                }
                status.update(label="Research Complete!", state="complete", expanded=False)

            except Exception as err:
                status.update(label="Error occurred during execution", state="error")
                st.error(f"Execution Error: {str(err)}")

# ------------------------------------------------------------------
# 7. DISPLAY RESULTS
# ------------------------------------------------------------------
if st.session_state["research_results"]:
    res = st.session_state["research_results"]
    
    st.divider()
    st.subheader("📄 Generated Market Intelligence Brief")
    
    # Download Button
    st.download_button(
        label="📥 Download Brief (.md)",
        data=res["brief"],
        file_name=f"MarketMind_Brief_{uuid.uuid4().hex[:6]}.md",
        mime="text/markdown"
    )
    
    # Render Report
    st.markdown(res["brief"])
    
    st.divider()
    # Inspection Tabs for Auditability / Human Approval Gate
    with st.expander("🔍 Inspect Agent Execution Pipeline (Audit Trail)"):
        tab1, tab2, tab3 = st.tabs(["Research Plan", "Evidence Analysis", "Quality Control"])
        
        with tab1:
            st.json(res["plan"])
            
        with tab2:
            st.write(res["analysis"])
            
        with tab3:
            st.write(res["qc"])
