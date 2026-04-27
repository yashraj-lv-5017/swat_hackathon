import streamlit as st
import pandas as pd
import plotly.express as px
from sentinel import run_sentinel_audit

# --- CONFIG ---
st.set_page_config(page_title="Axion Sentinel Pro", layout="wide", page_icon="🛡️")

# --- UI COMPONENT: ANALYTICS ---
def render_analytics(report):
    violations = report.get('violations', [])
    if violations:
        st.subheader("📊 Brand Health Analytics")
        df = pd.DataFrame(violations)
        
        if 'category' not in df.columns: df['category'] = 'General'
        if 'impact_score' not in df.columns: df['impact_score'] = 5

        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(df, names='category', title="Violation Distribution", hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(df, x='category', y='impact_score', color='category', title="Risk Severity")
            st.plotly_chart(fig2, use_container_width=True)

# --- MAIN LAYOUT ---
st.title("🛡️ Axion Sentinel: Enterprise Governance")
st.markdown("### 3x3 Content Adaptation Matrix")

# --- SIDEBAR: THE 3x3 PERMUTATION CONTROLS ---
with st.sidebar:
    st.header("🎯 Context Matrix")
    # THE 3 CHANNELS
    channel = st.selectbox(
        "Select Channel", 
        ["LinkedIn post", "Marketing email", "Press Release"],
        help="Changes formatting and emoji usage."
    )
    # THE 3 AUDIENCES
    audience = st.selectbox(
        "Select Audience", 
        ["Executive", "Practitioner", "Technical Lead"],
        help="Changes the complexity and value-proposition focus."
    )
    st.divider()
    show_debug = st.toggle("🔍 Judge's Mode (Show RAG Retrieval)")

source_text = st.text_area("Enter Draft Content:", height=150, placeholder="e.g., We leverage AI-powered tech to seamlessly help you...")

if st.button("🚀 Run Deep Audit & Adapt"):
    if not source_text:
        st.warning("Please provide text to audit.")
    else:
        with st.spinner(f"Adapting for {audience} on {channel}..."):
            report = run_sentinel_audit(source_text, channel, audience)
            
            # --- 1. HEALTH & INSIGHT METRICS ---
            score = report.get('brand_health_score', 0)
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Brand Health Score", f"{score}%", f"{score-100}%", delta_color="inverse")
            m2.metric("Violations Found", len(report.get('violations', [])))
            # This reflects the 3x3 permutation choice
            m3.metric("Current Mode", f"{audience} | {channel[:3]}")

            # --- 2. ANALYTICS ---
            render_analytics(report)

            st.divider()

            # --- 3. UPDATED TEXT VERSION (The core "Insight") ---
            st.subheader(f"🔄 Transformation: Optimized for {audience}")
            st.caption(f"Strategy: Adapting tone for {channel} guidelines.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### ❌ Original Draft")
                st.error(source_text)
            with col_b:
                st.markdown(f"#### ✅ {audience}-Approved version")
                # This is your "Updated Insight" text
                st.success(report.get('adapted_text', "No adaptation generated."))

            # --- 4. DETAILED CHANGE LOG ---
            if report.get('change_log'):
                with st.expander("📝 Strategic Reasoning (Explainability)", expanded=True):
                    st.table(report.get('change_log'))

            # --- 5. RAG LOGIC ---
            if show_debug:
                st.divider()
                st.subheader("🧠 RAG Retrieval Context")
                st.info(report.get('retrieved_context', "No context retrieved."))