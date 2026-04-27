import streamlit as st
import pandas as pd
import plotly.express as px
from sentinel import run_sentinel_audit

# --- CONFIG ---
st.set_page_config(page_title="Axion Sentinel Pro", layout="wide", page_icon="🛡️")

# --- UI COMPONENTS ---
def render_analytics(report):
    violations = report.get('violations', [])
    if violations:
        st.subheader("📊 Brand Health Analytics")
        df = pd.DataFrame(violations)
        
        # Safety for missing columns
        if 'category' not in df.columns: df['category'] = 'General'
        if 'impact_score' not in df.columns: df['impact_score'] = 5

        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(df, names='category', title="Violation Distribution", hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(df, x='category', y='impact_score', color='category', title="Risk Severity")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.success("✨ Content is 100% Brand Compliant!")

# --- MAIN LAYOUT ---
st.title("🛡️ Axion Sentinel: Enterprise Governance")

with st.sidebar:
    st.header("⚙️ Controls")
    channel = st.selectbox("Channel", ["LinkedIn post", "Marketing email", "Press Release"])
    audience = st.selectbox("Audience", ["Executive", "Practitioner", "Technical Lead"])
    st.divider()
    show_debug = st.toggle("🔍 Judge's Mode (Show RAG)")

source_text = st.text_area("Enter Draft Content:", height=150, placeholder="e.g., We leverage AI to seamlessly power workflows...")

if st.button("🚀 Run Deep Audit"):
    if not source_text:
        st.warning("Please provide text to audit.")
    else:
        with st.spinner("Sentinel is analyzing..."):
            report = run_sentinel_audit(source_text, channel, audience)
            
            # Metrics Row
            score = report.get('brand_health_score', 0)
            m1, m2, m3 = st.columns(3)
            m1.metric("Brand Health", f"{score}%", f"{score-100}%", delta_color="inverse")
            m2.metric("Violations Found", len(report.get('violations', [])))
            m3.metric("Persona", f"{audience}/{channel[:3]}")

            # Analytics Charts
            render_analytics(report)

            # Transformation Columns
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("❌ Original Draft")
                st.error(source_text)
            with col_b:
                st.subheader("✅ Axion-Approved")
                st.success(report.get('adapted_text'))

            # Judge's Mode RAG Logic
            if show_debug:
                st.divider()
                st.subheader("🧠 RAG Retrieval Context")
                st.info(report.get('retrieved_context', "No context retrieved."))

            # Change Log Table
            if report.get('change_log'):
                st.subheader("📝 Strategic Change Log")
                st.table(report.get('change_log'))