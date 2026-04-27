import os
import json
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# Client Setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

q_client = QdrantClient("localhost", port=6333)
COLLECTION_NAME = "axion_governance"

def run_sentinel_audit(source_text, channel="LinkedIn post", audience="Executive"):
    context_rules = "No specific rules found."
    
    # 1. VECTOR SEARCH (RAG)
    try:
        emb_res = client.embeddings.create(
            input=source_text,
            model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
        )
        vector = emb_res.data[0].embedding

        search_results = q_client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=5
        )
        
        if search_results.points:
            # Match the keys from your ingestion file ('rule_text' and 'section')
            context_rules = "\n".join([
                f"- {h.payload.get('rule_text')} (Ref: {h.payload.get('section')})" 
                for h in search_results.points
            ])
    except Exception as e:
        print(f"⚠️ Search failed: {e}")

    # 2. PERSONA MAPS
    channel_map = {
        "LinkedIn post": "Format: Punchy, high white-space, 2 emojis. Social tone.",
        "Marketing email": "Format: Personal, direct, clear CTA. Warm tone.",
        "Press Release": "Format: AP Style, objective, 3rd person. Institutional tone."
    }
    audience_map = {
        "Executive": "Focus: ROI, Strategy, Market Outcomes.",
        "Practitioner": "Focus: Workflow, Speed, Ease of Use.",
        "Technical Lead": "Focus: Scalability, Security, Architecture."
    }

    # 3. SYSTEM PROMPT
    system_prompt = f"""
    You are the Axion Brand Sentinel.
    
    TARGET: {channel} for {audience}.
    RULES: {context_rules}
    TONE GUIDE: {channel_map.get(channel)} | {audience_map.get(audience)}

    TASK:
    1. Identify violations. Categorize as: Terminology, Tone, Legal, or Formatting.
    2. Assign an 'impact_score' (1-10) per violation.
    3. Rewrite the text to be 100% compliant.

    RETURN JSON ONLY:
    {{
        "brand_health_score": int,
        "violations": [
            {{ "category": "str", "impact_score": int, "rule_id": "str", "text_found": "str", "fix": "str" }}
        ],
        "adapted_text": "str",
        "retrieved_context": "{context_rules}",
        "change_log": [{{ "from": "str", "to": "str", "reason": "str" }}]
    }}
    """

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": source_text}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"brand_health_score": 0, "violations": [], "adapted_text": f"Error: {str(e)}", "retrieved_context": context_rules}