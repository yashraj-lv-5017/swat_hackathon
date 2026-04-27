import streamlit as st
from sentinel import run_sentinel_audit

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Axion Sentinel Pro", layout="wide")

def render_metrics(report):
    score = report.get('brand_health_score', 0)
    cols = st.columns(4)
    cols[0].metric("Health Score", f"{score}%", f"{score-100}%", delta_color="inverse")
    cols[1].metric("Violations", len(report.get('violations', [])))
    cols[2].metric("Complexity", "High" if len(report.get('adapted_text')) > 500 else "Low")
    cols[3].metric("Engine", "GPT-5.4-Beta")

def render_explanation(report):
    with st.expander("🧪 Strategic Reasoning & Explainability", expanded=True):
        st.write("### Why these changes were made:")
        for log in report.get('change_log', []):
            st.markdown(f"**Modified:** `{log['from']}` → `{log['to']}`")
            st.caption(f"💡 *Reasoning:* {log['reason']}")

# --- MAIN UI ---
st.title("🛡️ Axion Sentinel: Enterprise Governance")

# Sidebar Module
with st.sidebar:
    st.header("Settings")
    channel = st.selectbox("Channel", ["LinkedIn post", "Marketing email", "Press Release"])
    audience = st.selectbox("Audience", ["Executive", "Practitioner", "Technical Lead"])

# Input Module
source_text = st.text_area("Draft Content", height=150)

if st.button("🚀 Run Deep Audit"):
    report = run_sentinel_audit(source_text, channel, audience)
    
    # Render Modular Components
    render_metrics(report)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Original")
        st.info(source_text)
    with col2:
        st.subheader("✅ Adapted")
        st.success(report.get('adapted_text'))
    
    render_explanation(report)