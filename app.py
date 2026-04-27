import streamlit as st
import pandas as pd
import plotly.express as px
from sentinel import run_sentinel_audit
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import diff_match_patch as dmp_module
import pdfplumber
from docx import Document
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Axion Sentinel Elite: Governance Engine",
    layout="wide",
    page_icon="🛡️"
)

# --- 2. SESSION STATE ---
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = []
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""

# --- 3. UTILITIES ---
def analyze_complexity(text):
    """Calculates average word length as a proxy for technical complexity."""
    words = text.split()
    if not words: return 0
    return round(sum(len(w) for w in words) / len(words), 2)

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.type in ["text/plain"]:
            text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text

def render_diff(old_text, new_text):
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diffs)
    html_result = ""
    for (flag, data) in diffs:
        if flag == 0: html_result += f"<span>{data}</span>"
        elif flag == 1: html_result += f"<span style='background-color: #d4edda; color: #155724; font-weight: bold;'>{data}</span>"
        elif flag == -1: html_result += f"<span style='background-color: #f8d7da; color: #721c24; text-decoration: line-through;'>{data}</span>"
    st.markdown(f"<div style='border: 1px solid #ddd; padding: 20px; border-radius: 10px; line-height: 1.8; background-color: white; color: black;'>{html_result}</div>", unsafe_allow_html=True)

def create_pdf_report(report, audience, complexity_delta):
    pdf = FPDF()
    pdf.add_page()
    def sanitize(text):
        if not text: return ""
        rep = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"}
        for k, v in rep.items(): text = text.replace(k, v)
        return str(text).encode("latin-1", "replace").decode("latin-1")

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, sanitize(f"Axion Governance Audit: {audience}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, sanitize(f"Brand Health Score: {report.get('brand_health_score', 0)}%"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, sanitize(f"Linguistic Shift: {complexity_delta}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, "Approved Content:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 8, sanitize(report.get('adapted_text', "")))
    return bytes(pdf.output())

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🎯 Context Matrix")
    channel = st.selectbox("Distribution Channel", ["LinkedIn post", "Marketing email", "Press Release"])
    audience = st.selectbox("Target Stakeholder", ["Executive", "Practitioner", "Technical Lead"])
    st.divider()
    st.subheader("📋 Session History")
    if st.session_state.audit_history:
        for entry in reversed(st.session_state.audit_history):
            st.caption(f"{entry['time']} | Score: {entry['score']}% ({entry['audience']})")
        if st.button("Clear Logs"):
            st.session_state.audit_history = []
            st.rerun()
    st.divider()
    show_debug = st.toggle("🔍 Trace Mode (RAG/Agent Logic)")

# --- 5. MAIN CONTENT ---
st.title("🛡️ Axion Sentinel: Enterprise Governance")
st.subheader("📁 Content Ingestion")
uploaded_file = st.file_uploader("Upload a Draft (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    extracted = extract_text_from_file(uploaded_file)
    if extracted: st.session_state.current_text = extracted

source_text = st.text_area("Input Draft Content:", value=st.session_state.current_text, height=180)

# --- 6. AUDIT EXECUTION ---
if st.button("🚀 Execute Strategic Audit", use_container_width=True):
    if not source_text:
        st.error("Buffer is empty. Please provide text or upload a file.")
    else:
        # PROGRESS BAR FEATURE
        my_bar = st.progress(0, text="Initializing Audit Engine...")
        time.sleep(0.4)
        my_bar.progress(25, text="🔍 Querying Axion Qdrant Database...")
        
        # CORE CALL
        report = run_sentinel_audit(source_text, channel, audience)
        
        my_bar.progress(60, text="🧠 Multi-Agent Compliance Check...")
        time.sleep(0.5)
        my_bar.progress(90, text="🔄 Finalizing Adaptation...")
        time.sleep(0.3)
        my_bar.progress(100, text="✅ Audit Complete")
        time.sleep(0.5)
        my_bar.empty()

        # Analytics
        orig_comp = analyze_complexity(source_text)
        new_comp = analyze_complexity(report.get('adapted_text', ''))
        comp_delta = round(new_comp - orig_comp, 2)
        
        # History
        st.session_state.audit_history.append({
            "time": time.strftime("%H:%M"),
            "score": report.get('brand_health_score', 0),
            "audience": audience
        })

        # METRICS DISPLAY
        score = report.get('brand_health_score', 0)
        conf = report.get('confidence_score', 65)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Health Score", f"{score}%", f"{score-100}%", delta_color="inverse")
        m2.metric("Audit Confidence", f"{conf}%")
        m3.metric("Linguistic Shift", f"{new_comp}", delta=comp_delta)
        m4.metric("Violations Found", len(report.get('violations', [])))

        # CHARTS
        if report.get('violations'):
            st.subheader("📊 Strategic Violation Analysis")
            df = pd.DataFrame(report['violations'])
            
            # Data Normalization for Charts
            if 'category' not in df.columns: 
                df['category'] = 'General'
            
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.pie(df, names='category', title="Violation Mix (By Category)", hole=0.5, 
                                      color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
            with c2:
                y_val = 'impact_score' if 'impact_score' in df.columns else None
                st.plotly_chart(px.bar(df, x='category', y=y_val, title="Risk Severity Density", 
                                      color='category', color_discrete_sequence=px.colors.qualitative.Safe), use_container_width=True)

        # TRANSFORMATION VIEW
        st.divider()
        st.subheader(f"🔄 Transformation Insight: {audience} Persona")
        render_diff(source_text, report.get('adapted_text', ''))

        # CHANGE LOG
        st.subheader("📝 Strategic Change Log")
        if report.get('change_log'):
            st.table(report.get('change_log'))
        else:
            st.info("No specific word-level changes documented.")

        # EXPORT
        pdf_bytes = create_pdf_report(report, audience, comp_delta)
        st.download_button("📥 Download Official Audit Report", data=pdf_bytes, file_name=f"Axion_Audit_{audience}.pdf", use_container_width=True)

        # DEBUG TRACE
        if show_debug:
            st.divider()
            with st.expander("🧠 System Logic Trace (JSON View)"):
                st.info(f"**Retrieved RAG Context:** {report.get('retrieved_context', 'N/A')}")
                st.json(report)