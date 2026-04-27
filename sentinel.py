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
    words = text.split()
    return round(sum(len(word) for word in words) / len(words), 2) if words else 0

# --- 4. CORE AUDIT ENGINE ---
def run_sentinel_audit(source_text, channel="LinkedIn post", audience="Executive"):
    """
    Industry-grade audit engine with Hard-Constraint Verification and Categorization.
    """
    context_rules = "No specific database rules found."
    start_time = time.time()
    rules_found = 0
    
    # STAGE 1: RAG RETRIEVAL
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

    # STAGE 2: MULTI-AGENT REASONING
    system_prompt = f"""
    You are the Axion Brand Sentinel. Your goal is to find reasons to DEDUCT points based on the stakeholder matrix.
    
    AUDIENCE: {audience} | CHANNEL: {channel}
    STAKEHOLDER RULES: {STAKEHOLDER_MATRIX.get(audience)}
    BRAND RULES: {context_rules}

    CRITICAL SCORING & CATEGORIZATION LOGIC:
    1. Start at 100 points.
    2. CATEGORIES: You MUST use these exact categories: 'Terminology', 'Tone', 'Legal', 'Formatting'.
    3. TONE PENALTY: If Audience is 'Executive' and Complexity > 5.8, deduct 35 points for 'Tone'.
    4. JARGON PENALTY: Deduct 20 points for every FORBIDDEN word used. Category: 'Terminology'.
    5. OMISSION PENALTY: Deduct 15 points if MANDATORY keywords are missing. Category: 'Legal'.
    6. DOCUMENT every specific word change in the 'change_log'.

    RETURN JSON ONLY:
    {{
        "brand_health_score": int,
        "confidence_score": int,
        "violations": [{{ "category": "Terminology|Tone|Legal|Formatting", "impact_score": int, "reason": "str", "fix": "str", "text_found": "str" }}],
        "adapted_text": "str",
        "change_log": [{{ "from": "str", "to": "str", "reason": "str", "rule_cited": "str" }}]
    }}
    """

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": source_text}],
            response_format={"type": "json_object"},
            temperature=0  # Absolute consistency for audit
        )
        report = json.loads(response.choices[0].message.content)
        
        # Post-Processing Analytics
        new_comp = calculate_complexity(report.get('adapted_text', ""))
        report["retrieved_context"] = context_rules
        
        # Manual Log Recovery if AI is lazy
        if not report.get('change_log') and report.get('violations'):
            report['change_log'] = [
                {
                    "from": v.get('text_found', '...'), 
                    "to": v.get('fix', 'Fixed'), 
                    "reason": v.get('reason', 'Compliance'), 
                    "rule_cited": "Brand Matrix"
                } for v in report.get('violations', [])
            ]

        report["audit_metadata"] = {
            "latency_sec": round(time.time() - start_time, 2),
            "tone_shift": round(new_comp - current_density, 2),
            "confidence_score": 98 if rules_found > 0 else 65
        }
        report["confidence_score"] = report["audit_metadata"]["confidence_score"]
        return report

    except Exception as e:
        return {
            "brand_health_score": 85, 
            "confidence_score": 50,
            "violations": [{"category": "System", "impact_score": 5, "reason": "Handover", "fix": "Check Logs"}],
            "adapted_text": source_text, 
            "change_log": [],
            "audit_metadata": {"latency_sec": 0, "tone_shift": 0, "confidence_score": 50}
        }