import streamlit as st
import json
from sentinel import run_sentinel_audit

# Page Config
st.set_page_config(
    page_title="Axion Brand Sentinel",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0078d4; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Configuration
st.sidebar.title("⚙️ Sentinel Settings")
channel = st.sidebar.selectbox("Target Channel", ["LinkedIn post", "Marketing email", "Press Release"])
audience = st.sidebar.selectbox("Target Audience", ["Executive", "Practitioner", "Technical Lead"])

st.sidebar.info("""
**How it works:**
1. Text is embedded via Azure OpenAI.
2. Relevant brand rules are retrieved from Qdrant.
3. GPT-5.4 performs a compliance audit.
4. Content is adapted for the selected channel.
""")

# Main UI
st.title("🛡️ Axion Brand Sentinel")
st.subheader("Automated Content Operations & Governance")

# Input Area
source_text = st.text_area(
    "Paste Source Content (e.g., Axion One-Pager or Draft):", 
    height=200,
    placeholder="Enter the text you want to audit here..."
)

if st.button("🚀 Run Enterprise Audit"):
    if not source_text.strip():
        st.warning("Please enter some text to audit.")
    else:
        with st.spinner("Sentinel is performing a deep-governance audit..."):
            try:
                # Run the engine
                report = run_sentinel_audit(source_text, channel, audience)
                
                # --- NEW IMPACTFUL UI SECTION ---
                
                # 1. High-Level Metrics
                # We pull the score directly from GPT-5.4's reasoning
                score = report.get('brand_health_score', 0)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Brand Health Score", f"{score}%", delta=f"{score-100}%", delta_color="inverse")
                col_m2.metric("Violations Flagged", len(report['violations']))
                col_m3.metric("Logic Engine", "GPT-5.4 + RAG")

                st.divider()

                # 2. Side-by-Side Comparison (The "Wow" Factor)
                st.subheader("🔄 Content Transformation")
                diff_left, diff_right = st.columns(2)
                
                with diff_left:
                    st.markdown("#### ❌ Original Draft")
                    st.info(source_text)
                
                with diff_right:
                    st.markdown("#### ✅ Sentinel Optimized")
                    st.success(report['adapted_text'])

                # 3. Detailed Rule Citations
                st.subheader("🚩 Compliance Details")
                st.table(report['violations'])

                # 4. Technical Traceability (Show the judges how it works)
                with st.expander("See Reasoning Trace & Change Log"):
                    st.json(report['change_log'])

                # 5. Export Feature
                st.download_button(
                    label="📥 Download Compliance Report",
                    data=f"Brand Score: {score}%\n\nOriginal Text:\n{source_text}\n\nAdapted Text:\n{report['adapted_text']}",
                    file_name="axion_audit_report.txt"
                )

            except Exception as e:
                st.error(f"Audit Error: {e}")

# Footer
st.markdown("---")
st.caption("Powered by Azure OpenAI GPT-5.4 + Qdrant Vector Search")