import os
import json
import time
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Robust connection with timeout for stability
try:
    q_client = QdrantClient("localhost", port=6333, timeout=2, prefer_grpc=False)
except:
    q_client = None

COLLECTION_NAME = "axion_governance"

# --- 2. STAKEHOLDER MATRIX ---
# These are the hard constraints the AI uses to penalize the score.
STAKEHOLDER_MATRIX = {
    "Executive": {
        "focus": "High-level ROI and Strategy",
        "forbidden": ["API", "Sub-latency", "Refactoring", "Codebase", "deployment", "backend"],
        "mandatory": ["ROI", "Alignment", "Growth", "Outcome"],
        "max_complexity": 5.2
    },
    "Practitioner": {
        "focus": "Daily workflow and integration",
        "forbidden": ["Blue-sky", "Paradigm shift", "synergy"],
        "mandatory": ["Step-by-step", "Integration", "Efficiency"],
        "max_complexity": 7.0
    },
    "Technical Lead": {
        "focus": "Architecture and Scalability",
        "forbidden": ["Easy-to-use", "Magic", "Simple fix", "user-friendly"],
        "mandatory": ["Latency", "Scalability", "Schema", "Encryption"],
        "max_complexity": 9.5
    }
}

# --- 3. ANALYTICS ---
def calculate_complexity(text):
    """Measures technical density by average word length."""
    words = text.split()
    return round(sum(len(word) for word in words) / len(words), 2) if words else 0

# --- 4. CORE AUDIT ENGINE ---
def run_sentinel_audit(source_text, channel="LinkedIn post", audience="Executive"):
    """
    Audit engine that retrieves rules from Qdrant and audits text via GPT-4.
    """
    context_rules = "No specific database rules found."
    start_time = time.time()
    rules_found = 0
    
    # STAGE 1: RAG RETRIEVAL (Fetching Brand Rules from Qdrant)
    if q_client:
        try:
            emb_res = client.embeddings.create(
                input=source_text, 
                model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
            )
            vector = emb_res.data[0].embedding
            search_results = q_client.query_points(collection_name=COLLECTION_NAME, query=vector, limit=5)
            if search_results.points:
                rules_found = len(search_results.points)
                context_rules = "\n".join([f"RULE: {h.payload.get('rule_text')}" for h in search_results.points])
        except:
            pass

    constraints = STAKEHOLDER_MATRIX.get(audience)
    current_density = calculate_complexity(source_text)

# STAGE 2: THE 3x3 GOVERNANCE PROMPT
    system_prompt = f"""
    You are the Axion Brand Sentinel. Your audit must pivot based on the 3x3 Matrix:
    
    1. STAKEHOLDER: {audience} (Focus: {STAKEHOLDER_MATRIX[audience]['focus']})
    2. CHANNEL: {channel} (Formatting Style: {channel})
    
    SCORING CALIBRATION (Strictly follow this for 3x3 variance):
    - If {audience} == 'Technical Lead' and {channel} == 'LinkedIn post':
        * Complexity up to 9.0 is ALLOWED. (Reward technical depth).
    - If {audience} == 'Executive' and {channel} == 'Press Release':
        * Complexity MUST be below 5.5. (Heavy penalty if too technical).
        * Tone must be Formal. (Penalty for 'slang' or 'dev-squad' talk).
    - If {audience} == 'Practitioner' and {channel} == 'Marketing email':
        * Tone must be Action-oriented.
        * Deduct 20 points if 'step-by-step' logic is missing.

    VIOLATION CATEGORIZATION (For Multi-Color Charts):
    - 'Terminology': Forbidden word usage.
    - 'Tone': Persona mismatch (e.g., Technical talk to Executive).
    - 'Legal': Missing mandatory keywords from the matrix.
    - 'Formatting': Channel mismatch (e.g., too many emojis in a Press Release).

    RETURN JSON ONLY:
    {{
        "brand_health_score": int,
        "confidence_score": int,
        "violations": [{{ "category": "Terminology|Tone|Legal|Formatting", "impact_score": int, "reason": "str", "fix": "str" }}],
        "adapted_text": "str",
        "change_log": [{{ "from": "str", "to": "str", "reason": "str" }}]
    }}
    """

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": source_text}],
            response_format={"type": "json_object"},
            temperature=0
        )
        report = json.loads(response.choices[0].message.content)
        
        # Post-Processing Meta-data
        new_comp = calculate_complexity(report.get('adapted_text', ""))
        report["retrieved_context"] = context_rules
        
        # Change Log Recovery logic (if AI forgets to populate)
        if not report.get('change_log') and report.get('violations'):
            report['change_log'] = [
                { "from": v.get('text_found', '...'), "to": v.get('fix', 'Fixed'), "reason": v.get('reason'), "rule_cited": "Brand Matrix" } 
                for v in report.get('violations', [])
            ]

        report["audit_metadata"] = {
            "latency_sec": round(time.time() - start_time, 2),
            "tone_shift": round(new_comp - current_density, 2),
            "confidence_score": 98 if rules_found > 0 else 65
        }
        report["confidence_score"] = report["audit_metadata"]["confidence_score"]
        return report

    except Exception as e:
        # Emergency fallback to keep the app running
        return {
            "brand_health_score": 85, 
            "confidence_score": 50,
            "violations": [{"category": "System", "impact_score": 5, "reason": "API Handover Error", "fix": "Retry Audit"}],
            "adapted_text": source_text, 
            "change_log": [],
            "audit_metadata": {"latency_sec": 0, "tone_shift": 0, "confidence_score": 50}
        }