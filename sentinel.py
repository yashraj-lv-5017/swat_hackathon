import os
import json
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# Client setup using your specific credentials
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

q_client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "axion_governance"

def run_sentinel_audit(source_text, channel="LinkedIn post", audience="Executive"):
    context_rules = "No specific rules found in database."
    
    try:
        # 1. Embedding logic using your specific deployment name
        embedding_response = client.embeddings.create(
            input=source_text,
            model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
        )
        search_emb = embedding_response.data[0].embedding

        # 2. Qdrant Search
        search_results = q_client.query_points(
            collection_name=COLLECTION_NAME,
            query=search_emb,
            limit=5
        )
        
        if search_results.points:
            context_rules = "\n".join([
                f"- {h.payload['rule_text']} (Ref: {h.payload['section']})" 
                for h in search_results.points
            ])
    except Exception as e:
        print(f"⚠️ Vector Search failed: {e}")

    # 3. 9-Combination Persona Logic
    channel_map = {
        "LinkedIn post": "Short, bold chunks. 2 emojis. Use white space.",
        "Marketing email": "Personal tone. Focus on 'You'. Clear CTA.",
        "Press Release": "Formal, objective, 3rd person. No emojis."
    }
    audience_map = {
        "Executive": "Focus on ROI & Market Strategy.",
        "Practitioner": "Focus on daily efficiency & ease.",
        "Technical Lead": "Focus on scalability & architecture."
    }

    # 4. The System Prompt
    system_prompt = f"""
    You are the Axion Brand Sentinel. 
    Audit this text based on these rules: {context_rules}
    Pivot the tone for a {audience} on {channel}.
    Guidelines: {channel_map.get(channel)} | {audience_map.get(audience)}
    
    Return JSON only:
    {{
        "brand_health_score": int,
        "violations": [{{ "rule_id": "str", "text_found": "str", "fix": "str" }}],
        "adapted_text": "str",
        "change_log": []
    }}
    """

    # 5. Chat Completion logic using your specific deployment name
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": source_text}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        return {
            "brand_health_score": 0,
            "violations": [{"rule_id": "ERR", "text_found": "N/A", "fix": str(e)}],
            "adapted_text": "Connection Error. Check terminal.",
            "change_log": []
        }