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

if st.button("🚀 Run Audit & Adaptation"):
    if not source_text.strip():
        st.warning("Please enter some text to audit.")
    else:
        with st.spinner("Sentinel is auditing against brand guidelines..."):
            try:
                # Run the engine
                report = run_sentinel_audit(source_text, channel, audience)
                
                # Layout for Results
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.success("✅ Compliance Audit Complete")
                    st.write("### 🚩 Rule Violations")
                    if report['violations']:
                        st.table(report['violations'])
                    else:
                        st.write("No violations found! The text is brand-compliant.")

                    st.write("### 📝 Change Log")
                    st.json(report['change_log'])

                with col2:
                    st.info(f"✨ Adapted for {channel}")
                    st.write("### Final Content")
                    st.markdown(f"```\n{report['adapted_text']}\n```")
                    
                    st.download_button(
                        label="Download Adapted Content",
                        data=report['adapted_text'],
                        file_name=f"axion_{channel.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Powered by Azure OpenAI GPT-5.4 + Qdrant Vector Search")