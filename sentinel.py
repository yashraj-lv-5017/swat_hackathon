import os
import json
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load credentials
load_dotenv()

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Initialize Qdrant Client
q_client = QdrantClient("localhost", port=6333)
COLLECTION_NAME = "axion_governance"

def run_sentinel_audit(source_text, channel="LinkedIn post", audience="Executive"):
    """
    RAG-driven Engine: Audits text against brand rules and adapts it for specific channels.
    """
    
    # 1. RETRIEVAL: Convert source text to embedding to find relevant rules
    embedding_response = client.embeddings.create(
        input=source_text,
        model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    )
    search_emb = embedding_response.data[0].embedding

    # 2. SEARCH: Query Qdrant for the top 5 most relevant brand rules
    # Using the updated query_points method to avoid AttributeError
    search_results = q_client.query_points(
        collection_name=COLLECTION_NAME,
        query=search_emb,
        limit=5
    )
    hits = search_results.points
    
    # Format rules for the prompt (matching the keys from ingest_rules.py)
    context_rules = "\n".join([
        f"- {h.payload['rule_text']} (Ref: {h.payload['section']})" 
        for h in hits
    ])

    # 3. REASONING: Use GPT-5.4 to audit and adapt based on retrieved rules
    system_prompt = f"""
    You are the Axion Brand Sentinel. Your goal is to audit content and ensure brand compliance.

    ### RETRIEVED BRAND RULES:
    {context_rules}

    ### TARGET PARAMETERS:
    - Target Channel: {channel}
    - Target Audience: {audience}

    ### YOUR TASKS:
    1. Identify every violation of the brand rules in the source text.
    2. Rewrite the content perfectly for {channel} and {audience}.
       - If LinkedIn: Use 1-2 sentence paragraphs, maximum white space, and a direct tone.
    3. Generate a change log for every modification.

    ### OUTPUT FORMAT:
    You MUST return a valid JSON object:
    {{
        "brand_health_score": 85, 
        "violations": [
            {{ "text_found": "phrase", "rule_id": "§ section", "fix": "correction", "severity": "High/Medium" }}
        ],
        "adapted_text": "Rewritten content",
        "change_log": [
            {{ "from": "old", "to": "new", "reason": "why" }}
        ]
    }}
    """

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"SOURCE CONTENT TO AUDIT:\n{source_text}"}
        ],
        response_format={ "type": "json_object" }
    )

    return json.loads(response.choices[0].message.content)

# Test block for manual verification
if __name__ == "__main__":
    # Test text containing deliberate violations (AI-powered, leverage, seamlessly)
    test_text = "Our platform is AI-powered and helps you leverage data seamlessly."
    
    print("🔬 Running Test Audit with GPT-5.4...")
    try:
        result = run_sentinel_audit(test_text)
        print("\n✅ AUDIT SUCCESSFUL. RESULTS:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error during audit: {e}")