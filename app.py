import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: #111111;
}

.stApp { background: #ffffff; }

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1100px; }

/* ── Hero header ── */
.hero { text-align: left; padding: 1.25rem 0 0.5rem; }
.hero-eyebrow { font-family: 'Poppins',sans-serif; font-size: 0.72rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#c62828; margin-bottom:0.5rem; }
.hero h1, .hero h1 span { font-family: 'Poppins', sans-serif; font-size: clamp(1.6rem, 3.4vw, 2.4rem); font-weight:600; color:#c62828 !important; margin:0 0 0.25rem; }
.hero-sub { font-size:0.95rem; color:#6b6b6b; max-width: 640px; margin:0; }

/* ── Divider ── */
.divider { height:1px; background: #efefef; margin:1.25rem 0 1.25rem; }

/* ── Input card ── */
.input-card { background: transparent; border: none; padding: 0.25rem 0; margin-bottom: 1rem; }

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input { background: #ffffff !important; border: 1px solid #e6e6e6 !important; border-radius: 8px !important; color: #111111 !important; font-family: 'Poppins', sans-serif !important; font-size: 1rem !important; padding: 0.6rem 0.9rem !important; }
.stTextInput > div > div > input:focus { border-color: #c62828 !important; box-shadow: 0 8px 22px rgba(198,40,40,0.06) !important; }
.stTextInput > label { font-size:0.75rem; color:#c62828; font-weight:600; }

/* ── Button ── */
.stButton > button { background: #c62828 !important; color: #fff !important; font-weight:600 !important; border-radius:8px !important; padding:0.55rem 1rem !important; box-shadow: 0 6px 18px rgba(198,40,40,0.08); width:100%; }
.stButton > button:hover { box-shadow: 0 10px 26px rgba(198,40,40,0.12) !important; transform: translateY(-1px) !important; }

/* ── Pipeline step cards ── */
.step-card { background: #ffffff; border: 1px solid #f1f1f1; border-radius: 10px; padding: 1rem; margin-bottom: 0.9rem; }
.step-card.active { border-color: rgba(198,40,40,0.12); }
.step-card.done { border-color: rgba(80,200,120,0.12); }
.step-card::before { display:none; }
.step-header { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem; }
.step-num { font-family: 'Poppins',sans-serif; font-size:0.72rem; font-weight:700; color:#c62828; }
.step-title { font-weight:600; font-size:0.98rem; color:#111111; }
.step-status { margin-left:auto; font-size:0.75rem; color:#6b6b6b; }

/* ── Result panels ── */
.result-panel { background:#ffffff; border:1px solid #f1f1f1; border-radius:10px; padding:1rem; margin-top:0.75rem; }
.result-panel-title { font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#c62828; margin-bottom:0.75rem; border-bottom:1px solid #f3f3f3; padding-bottom:0.5rem; }
.result-content { font-size:0.95rem; line-height:1.6; color:#333333; }

/* ── Report & feedback panels ── */
.report-panel { background:#ffffff; border:1px solid #f1f1f1; border-radius:10px; padding:1rem; margin-top:0.75rem; }
.feedback-panel { background:#ffffff; border:1px solid #f1f1f1; border-radius:10px; padding:1rem; margin-top:0.75rem; }
.panel-label { font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.75rem; }
.panel-label.orange { color:#c62828; border-bottom:1px solid #f3f3f3; }
.panel-label.green { color:#50c878; border-bottom:1px solid #f3f3f3; }

/* ── Status / spinner */
.stSpinner > div { color: #c62828 !important; }

/* ── Expander */
details summary { font-family:'Poppins',sans-serif !important; font-size:0.9rem !important; color:#6b6b6b !important; }

/* ── Section heading */
.section-heading { font-family:'Poppins',sans-serif; font-size:1.1rem; font-weight:700; color:#c62828; margin:1.25rem 0 0.75rem; }

.notice { font-size:0.82rem; color:#6b6b6b; text-align:center; margin-top:2rem; }
</style>
""", unsafe_allow_html=True)

# ── Markdown color overrides (headings red, body black) ──
st.markdown("""
<style>
.stMarkdown h1, .stMarkdown h1 span, .stMarkdown h1 div,
.stMarkdown h2, .stMarkdown h2 span, .stMarkdown h2 div,
.stMarkdown h3, .stMarkdown h3 span, .stMarkdown h3 div,
.stMarkdown h4, .stMarkdown h4 span, .stMarkdown h4 div,
.stMarkdown h5, .stMarkdown h5 span, .stMarkdown h5 div,
.stMarkdown h6, .stMarkdown h6 span, .stMarkdown h6 div {
    color: #c62828 !important;
}
.stMarkdown p, .stMarkdown li, .stMarkdown a {
    color: #111111 !important;
}
/* Also scope for report-panel if present */
.report-panel h1, .report-panel h1 span, .report-panel h1 div,
.report-panel h2, .report-panel h2 span, .report-panel h2 div,
.report-panel h3, .report-panel h3 span, .report-panel h3 div {
    color: #c62828 !important;
}
.report-panel, .report-panel p, .report-panel li { color: #111111 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;
            padding:0.25rem 0.7rem;
            font-size:0.75rem;
            color:#a09890;
            font-family:'DM Sans',sans-serif;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        # figure out which steps are done
        if step in r:
            return "done"
        # which step is running now (first not in r)
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
    st.rerun() if False else None   # keep inline for now

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)