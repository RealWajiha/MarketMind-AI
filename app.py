import json
import uuid
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.agents.evidence_analyst import EvidenceAnalyst
from src.agents.planner import ResearchPlanner
from src.agents.quality_control import QualityControlAgent
from src.agents.report_generator import ReportGenerator
from src.agents.request_analyser import RequestAnalyser
from src.agents.researcher import ResearchAgentLoop
from src.agents.synthesis import SynthesisAgent
from src.approval.cli_gate import HumanApprovalGate
from src.llm.client import LLMClient
from src.llm.usage import UsageTracker
from src.state.research_state import ResearchState, ScopeObject

st.set_page_config(page_title="MarketMind AI - Research Workbench", layout="wide")

st.title("MarketMind AI: Autonomous Business Research Agent")
st.caption("AAI-412 Capstone Practical Implementation | OpenAI API + Custom Tool Loop")

# Sidebar Configuration
st.sidebar.header("Execution Controls")
run_cost_limit = st.sidebar.number_input("Cost Ceiling ($)", min_value=0.5, max_value=10.0, value=2.5, step=0.5)
max_iterations = st.sidebar.slider("Max Loop Iterations", 3, 20, 10)

if "state" not in st.session_state:
    st.session_state.state = None
if "report" not in st.session_state:
    st.session_state.report = None

# Tabs for workflow stages
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Request & Scope", "2. Research Plan", "3. Agent Execution & Logs", "4. Quality Control", "5. Final Report & Gate"
])

with tab1:
    st.subheader("Initiate Business Intelligence Brief")
    raw_request = st.text_area(
        "Client Request Prompt",
        value="Research the market for AI-powered customer support software, key competitors, pricing models, and entry risks.",
        height=100
    )

    if st.button("Analyse Request & Generate Scope", type="primary"):
        usage = UsageTracker()
        client = LLMClient(usage_tracker=usage)
        analyser = RequestAnalyser(client)
        
        with st.spinner("Analyzing request scope & ambiguities..."):
            scope = analyser.analyze(raw_request)
            run_id = f"RUN-{uuid.uuid4().hex[:6]}"
            st.session_state.state = ResearchState(run_id=run_id, scope=scope)
            st.success("Scope Analysis Completed!")

    if st.session_state.state:
        st.json(st.session_state.state.scope.model_dump())

with tab2:
    st.subheader("Research Plan & Sub-Question Breakdown")
    if st.session_state.state and not st.session_state.state.plan:
        if st.button("Generate Research Plan"):
            usage = UsageTracker()
            client = LLMClient(usage_tracker=usage)
            planner = ResearchPlanner(client)
            
            with st.spinner("Decomposing scope into research plan..."):
                plan = planner.create_plan(st.session_state.state.scope)
                st.session_state.state.plan = plan
                for obj in plan.objectives:
                    for sq in obj.sub_questions:
                        st.session_state.state.question_status[sq.id] = "open"
                st.rerun()

    if st.session_state.state and st.session_state.state.plan:
        st.write(f"**Geography:** {st.session_state.state.plan.geography} | **Horizon:** {st.session_state.state.plan.time_horizon}")
        for obj in st.session_state.state.plan.objectives:
            with st.expander(f"Objective {obj.id}: {obj.title}", expanded=True):
                st.write(obj.description)
                for sq in obj.sub_questions:
                    status = st.session_state.state.question_status.get(sq.id, "open")
                    st.write(f"- `{sq.id}`: {sq.question} (Status: **{status}**)")

with tab3:
    st.subheader("Autonomous Research Loop")
    if st.session_state.state and st.session_state.state.plan:
        if st.button("Run Research Agent Loop", type="primary"):
            usage = UsageTracker()
            client = LLMClient(usage_tracker=usage)
            analyst = EvidenceAnalyst(client)
            loop = ResearchAgentLoop(client, analyst)
            
            with st.spinner("Agent calling tools, gathering evidence, and analyzing claims..."):
                loop.run_loop(st.session_state.state)
                st.success("Research Loop Execution Finished!")

        st.metric("Total Cumulative Cost ($)", f"${st.session_state.state.cumulative_cost_usd:.4f}")
        st.metric("Total Tool Calls", st.session_state.state.tool_call_count)
        
        st.markdown("### Tool Call History")
        for log in st.session_state.state.tool_history:
            st.text(f"[{log.call_id}] Tool: {log.tool_name} | Error: {log.error}")
            st.json({"args": log.arguments, "result": log.result})

with tab4:
    st.subheader("Quality Control & Defect Inspector")
    if st.session_state.state and st.session_state.state.evidence_store:
        if st.button("Run Quality Control Check"):
            usage = UsageTracker()
            client = LLMClient(usage_tracker=usage)
            qc_agent = QualityControlAgent(client)
            
            with st.spinner("Checking claims, source references, and contradictions..."):
                verdict = qc_agent.run_qc(st.session_state.state)
                st.session_state.qc_verdict = verdict
                st.rerun()

        if "qc_verdict" in st.session_state:
            v = st.session_state.qc_verdict
            st.write(f"**QC Status Pass:** {v.passed}")
            for defect in v.defects:
                st.warning(f"[{defect.severity.upper()}] {defect.defect_type} at {defect.location}: {defect.description}")

with tab5:
    st.subheader("Final Synthesis & Human Approval Gate")
    if st.session_state.state and st.session_state.state.evidence_store:
        if st.button("Synthesise & Assemble Report"):
            usage = UsageTracker()
            client = LLMClient(usage_tracker=usage)
            synth_agent = SynthesisAgent(client)
            report_gen = ReportGenerator()
            
            with st.spinner("Synthesising evidence into structured report..."):
                findings = synth_agent.synthesize(st.session_state.state)
                report = report_gen.assemble(st.session_state.state, findings)
                st.session_state.report = report
                st.success("Report Assembly Complete!")

    if st.session_state.report:
        rep = st.session_state.report
        st.markdown(f"## {rep.research_objective}")
        st.markdown(f"**Executive Summary:** {rep.executive_summary}")
        
        st.markdown("### Key Trends")
        for trend in rep.key_trends:
            st.write(f"- **[{trend.claim_type.value.upper()}]** {trend.statement} (Evidence: {trend.evidence_ids})")

        st.markdown("### Competitor Matrix")
        matrix_data = []
        for cell in rep.competitor_analysis.cells:
            matrix_data.append({"Entity": cell.entity, "Attribute": cell.attribute, "Value": cell.value})
        st.table(matrix_data)

        st.markdown("---")
        st.subheader("Human Approval Gate (Mandatory Control)")
        
        col1, col2 = st.columns(2)
        with col1:
            approver_id = st.text_input("Approver ID / Name", value="Senior_Partner_01")
            approval_notes = st.text_area("Reviewer Notes", value="Verified claims against corpus citations.")
        
        with col2:
            decision = st.radio(
                "Select Approval Action:",
                options=["approve", "reject", "request_research", "modify_scope"]
            )
            
            if st.button("Submit Decision", type="primary"):
                updated_report = HumanApprovalGate.process_decision(
                    report=st.session_state.report,
                    decision=decision,
                    approver_id=approver_id,
                    notes=approval_notes
                )
                st.session_state.report = updated_report
                st.success(f"Action '{decision.upper()}' recorded by {approver_id}!")
                st.json(updated_report.approval.model_dump())