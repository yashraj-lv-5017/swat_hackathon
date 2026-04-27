import streamlit as st
import pandas as pd
import plotly.express as px
from sentinel import run_sentinel_audit
from fpdf import FPDF
import diff_match_patch as dmp_module
import pdfplumber
from docx import Document
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Axion Sentinel: Multi-Modal Governance",
    layout="wide",
    page_icon="🛡️"
)

# --- 2. UNIVERSAL FILE EXTRACTOR (NEWLY ADDED) ---
def extract_text_from_file(uploaded_file):
    """Detects file type and extracts raw text."""
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
        else:
            st.error("Unsupported file format.")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text

# --- 3. UTILITY: VISUAL DIFF ENGINE ---
def render_diff(old_text, new_text):
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diffs)
    html_result = ""
    for (flag, data) in diffs:
        if flag == 0: html_result += f"<span>{data}</span>"
        elif flag == 1: html_result += f"<span style='background-color: #d4edda; color: #155724; font-weight: bold;'>{data}</span>"
        elif flag == -1: html_result += f"<span style='background-color: #f8d7da; color: #721c24; text-decoration: line-through;'>{data}</span>"
    st.markdown(f"<div style='border: 1px solid #ddd; padding: 20px; border-radius: 10px; line-height: 1.8;'>{html_result}</div>", unsafe_allow_html=True)

# --- 4. UTILITY: PDF EXPORT ENGINE ---
def create_pdf_report(report, original_text):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    safe_width = 180 

    def sanitize(text):
        if not text: return ""
        return str(text).encode("latin-1", "replace").decode("latin-1").replace("?", " ")

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(safe_width, 10, "Axion Sentinel: Brand Governance Audit", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    score = sanitize(report.get('brand_health_score', 0))
    pdf.cell(safe_width, 10, f"Final Brand Health Score: {score}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(safe_width, 10, "Approved Adaptation:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    clean_adapted = sanitize(report.get('adapted_text', ""))
    pdf.multi_cell(safe_width, 8, clean_adapted)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(safe_width, 10, "Strategic Changes Made:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    for change in report.get('change_log', []):
        reason = sanitize(change.get('reason', 'N/A'))
        to_text = sanitize(change.get('to', 'N/A'))
        pdf.multi_cell(safe_width, 6, f"- {reason} (Updated to: {to_text})")
    
    return bytes(pdf.output())

# --- 5. SIDEBAR & MATRIX ---
with st.sidebar:
    st.header("🎯 Context Matrix")
    channel = st.selectbox("Distribution Channel", ["LinkedIn post", "Marketing email", "Press Release"])
    audience = st.selectbox("Target Stakeholder", ["Executive", "Practitioner", "Technical Lead"])
    st.divider()
    show_debug = st.toggle("🔍 Judge's Mode (RAG Traceability)")
    st.info(f"Mode: {audience} | {channel}")

# --- 6. MAIN CONTENT & FILE INGESTION ---
st.title("🛡️ Axion Sentinel: Enterprise Governance")

# File Upload Section
st.subheader("📁 Content Ingestion")
uploaded_file = st.file_uploader("Upload a Draft (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

# Extract text if file is uploaded
extracted_text = ""
if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    if extracted_text:
        st.success("✅ File text extracted!")

source_text = st.text_area(
    "Input Draft Content:", 
    value=extracted_text, # Autofills if file uploaded
    height=180, 
    placeholder="Enter copy or upload a file above..."
)

# --- 7. AUDIT EXECUTION ---
if st.button("🚀 Execute Strategic Audit", use_container_width=True):
    if not source_text:
        st.error("Please provide content to audit.")
    else:
        with st.spinner("Analyzing against Axion Governance Brain..."):
            report = run_sentinel_audit(source_text, channel, audience)
            
            # Metrics
            score = report.get('brand_health_score', 0)
            m1, m2, m3 = st.columns(3)
            m1.metric("Brand Health Score", f"{score}%", f"{score-100}%", delta_color="inverse")
            m2.metric("Critical Violations", len(report.get('violations', [])))
            m3.metric("Persona Alignment", "High" if score > 80 else "Needs Improvement")

            # Charts
            if report.get('violations'):
                st.subheader("📊 Strategic Violation Analysis")
                df = pd.DataFrame(report['violations'])
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.pie(df, names='category', title="Violation Types", hole=0.5), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df, x='category', y='impact_score', color='category', title="Risk Severity"), use_container_width=True)

            # Transformation (The Visual Diff)
            st.divider()
            st.subheader(f"🔄 Transformation Insight: {audience} Perspective")
            render_diff(source_text, report.get('adapted_text', ''))

            # Change Log & Export
            st.subheader("📝 Strategic Change Log")
            st.table(report.get('change_log', []))

            pdf_bytes = create_pdf_report(report, source_text)
            st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="Axion_Audit.pdf", mime="application/pdf")

            # Judge's Mode
            if show_debug:
                st.divider()
                st.subheader("🧠 RAG Internal Logic Trace")
                st.info(report.get('retrieved_context', "No context retrieved."))
                st.json(report)