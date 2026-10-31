import streamlit as st
from orchestrator import run_pipeline, planner, topo_sort

# --- PAGE CONFIG ---
st.set_page_config(page_title="NEXUS AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FAFAFA !important; font-family: 'Inter', sans-serif; }
    .agent-card {
        padding: 10px 15px; border-radius: 8px; margin-bottom: 8px;
        font-family: monospace; display: flex; align-items: center;
        justify-content: space-between; background-color: #1E232E;
        border-left: 4px solid #4B5563;
    }
    .agent-running { border-left-color: #3B82F6; background-color: #1E3A8A; }
    .agent-done { border-left-color: #10B981; background-color: #064E3B; }
    .agent-skipped { border-left-color: #EF4444; opacity: 0.5; }
    .agent-retry { border-left-color: #F59E0B; background-color: #78350F; }
    .stButton>button {
        background-color: #6366F1; color: white; border-radius: 8px;
        height: 50px; font-weight: bold; font-size: 16px; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #4F46E5; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("NEXUS Engine")
    st.markdown("**Autonomous Multi-Agent Problem Solver**")
    st.divider()
    
    # Create a placeholder for the metric
    time_metric = st.empty()
    
    st.markdown("### Architecture")
    st.markdown("- 🧠 **Planner:** Generates DAG\n- 🚦 **Feasibility:** Go / No-Go Gate\n- 📝 **Reqs & Design:** Spec generation\n- 💻 **Coder & Reviewer:** Code + Retry loop\n- 🧪 **Tester & Writer:** QA + Final Report")
    st.divider()
    st.caption("Powered by Gemini 3.5 Flash")

# --- HEADER ---
st.title("🧠 NEXUS")
st.markdown("#### Describe your software project. The multi-agent system will plan, design, code, and review it.")
st.divider()

# --- INPUT ---
brief = st.text_area(
    "Project Brief:", height=130,
    placeholder="e.g. Build a bookstore REST API with login and CRUD for books. Deadline 3 weeks, 2 devs, tight budget.",
    label_visibility="collapsed"
)

# --- HELPER FUNCTIONS ---
def extract_report(results: dict):
    keys = ("project_report", "report", "markdown", "final_report", "output", "raw_output")
    section_titles = {"feasibility", "requirements", "methodology", "architecture", "code", "review", "tests", "maintenance notes"}
    for v in results.values():
        if isinstance(v, dict):
            for k in keys:
                if k in v and v[k]: return v[k]
            if any(str(k).lower() in section_titles for k in v.keys()):
                return "\n\n".join(f"## {k}\n\n{val}" for k, val in v.items())
        elif isinstance(v, str) and len(v) > 100:
            return v
    return None

def get_icon(s):
    return {"running": "🔄", "done": "✅", "retry": "🔁", "pending": "⏸", "skipped": "⏭"}.get(s, "⏳")

def get_class(s):
    return f"agent-{s}" if s in ["running", "done", "skipped", "retry"] else ""

def render_trace_html(planned, statuses):
    html = ""
    for a in planned:
        s = statuses.get(a, "pending")
        html += f"""<div class="agent-card {get_class(s)}">
            <span><b>{a.upper()}</b></span>
            <span>{get_icon(s)} {s.capitalize()}</span>
        </div>"""
    return html

def get_tab_name(tid, planned_agents):
    try:
        idx = int(tid) - 1
        if 0 <= idx < len(planned_agents):
            return planned_agents[idx].capitalize()
    except:
        pass
    return f"Agent {tid}"

# --- RUN ---
if st.button("🚀 Execute Pipeline") and brief.strip():
    
    try:
        planned = [t["agent"] for t in topo_sort(planner(brief))]
    except Exception as e:
        st.error(f"Planner failed: {e}")
        st.stop()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Agent Trace")
        trace_ph = st.empty()
        trace_ph.markdown(render_trace_html(planned, {}), unsafe_allow_html=True)

    statuses = {}
    results = {}

    def trace_callback(status, agent):
        statuses[agent] = status
        trace_ph.markdown(render_trace_html(planned, statuses), unsafe_allow_html=True)

    try:
        with st.spinner("Agents are thinking..."):
            results, exec_time = run_pipeline(brief, trace_callback=trace_callback)
            
        # Update the sidebar metric dynamically
        time_metric.metric(label="Last Run Time", value=f"{exec_time} sec")
        st.sidebar.metric(label="API Calls (Agents)", value=len(results))
            
        final_statuses = dict(statuses)
        for a in planned:
            if a not in final_statuses:
                final_statuses[a] = "skipped"
        trace_ph.markdown(render_trace_html(planned, final_statuses), unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Pipeline error: {e}")
        st.stop()

    if not results:
        st.stop()

    report = extract_report(results)

    with col2:
        st.markdown("### 📋 Output")
        
        tab_labels = ["📋 Final Report"] + [get_tab_name(k, planned) for k in results.keys()]
        tabs = st.tabs(tab_labels)
        
        with tabs[0]:
            if report:
                st.markdown(report)
            else:
                st.warning("Writer agent failed to generate a markdown report. Showing last output:")
                st.json(list(results.values())[-1])

        for i, (tid, out) in enumerate(results.items(), start=1):
            with tabs[i]:
                if isinstance(out, dict) and "raw_output" in out:
                    out = out["raw_output"]

                if isinstance(out, str):
                    st.markdown(out)
                    continue

                if isinstance(out, dict):
                    if "code" in out or "filename" in out:
                        filename = out.get("filename", "script.py")
                        st.markdown(f"**File:** `{filename}`")
                        code_text = out.get("code", "")
                        st.code(code_text, language="python")
                        if out.get("explanation"):
                            st.markdown("**Explanation:**")
                            st.write(out["explanation"])
                        
                    elif "verdict" in out:
                        severity = str(out.get("severity", "UNKNOWN")).upper()
                        if str(out["verdict"]).upper() == "PASS":
                            st.success("✅ Code Review Passed")
                        else:
                            st.error(f"❌ Code Review Failed — Severity: {severity}")
                            if not out.get("correctness_issues") and not out.get("security_issues"):
                                st.markdown("#### 📝 Reviewer Notes")
                                for k, v in out.items():
                                    if k not in ["verdict", "severity"]:
                                        st.markdown(f"**{k.capitalize()}:** {v}")
                            else:
                                if out.get("correctness_issues"):
                                    st.markdown("#### 🐛 Correctness Issues")
                                    for issue in out["correctness_issues"]: 
                                        st.write(f"- {issue}")
                                if out.get("security_issues"):
                                    st.markdown("#### 🔒 Security Issues")
                                    for issue in out["security_issues"]: 
                                        if isinstance(issue, dict):
                                            st.write(f"- **{issue.get('type', 'Vuln')}** at `{issue.get('location', 'code')}`: {issue.get('fix', '')}")
                                        else:
                                            st.write(f"- {issue}")
                            
                            # ---- HUMAN IN THE LOOP ----
                            st.markdown("---")
                            st.markdown("### 🧑‍💻 Human-in-the-Loop (HITL)")
                            st.info("The Reviewer Agent flagged this code. Human intervention required.")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Override & Approve Code"):
                                st.success("Human approved. Proceeding...")
                            if c2.button("❌ Reject & Retry"):
                                st.warning("Human rejected. Re-queueing task...")
                            # -------------------------
                    
                    else:
                        st.json(out)
                else:
                    st.write(out)