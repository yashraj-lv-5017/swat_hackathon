import streamlit as st
from sentinel import run_sentinel_audit

# Config
st.set_page_config(page_title="Axion Sentinel", page_icon="🛡️", layout="wide")

# Sidebar
st.sidebar.title("🛡️ Sentinel Controls")
channel = st.sidebar.selectbox("Channel", ["LinkedIn post", "Marketing email", "Press Release"])
audience = st.sidebar.selectbox("Audience", ["Executive", "Practitioner", "Technical Lead"])

# Header
st.title("🛡️ Axion Brand Sentinel")
st.caption(f"Currently Auditing for: **{audience}** via **{channel}**")

# Input
source_text = st.text_area("Source Content:", height=150)

if st.button("🚀 Run Enterprise Audit"):
    if not source_text:
        st.warning("Please enter text.")
    else:
        with st.spinner("Processing..."):
            report = run_sentinel_audit(source_text, channel, audience)
            
            # Metrics
            score = report.get('brand_health_score', 0)
            c1, c2, c3 = st.columns(3)
            c1.metric("Brand Health", f"{score}%", f"{score-100}%", delta_color="inverse")
            c2.metric("Violations", len(report.get('violations', [])))
            c3.metric("Context", f"{audience}/{channel[:3]}")

            st.divider()

            # Comparison
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("❌ Original")
                st.error(source_text)
            with col_b:
                st.subheader("✅ Adapted")
                st.success(report.get('adapted_text'))

            # Table
            st.subheader("🚩 Audit Findings")
            st.table(report.get('violations'))

            with st.expander("View Full JSON Trace"):
                st.json(report)