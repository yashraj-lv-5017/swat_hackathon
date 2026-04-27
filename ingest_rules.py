import os
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from dotenv import load_dotenv

# Load credentials from .env
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

def ingest_brand_guidelines():
    print("🚀 Starting Brand Guideline Ingestion...")

    # 1. Clean up and Setup Collection (Modern Method)
    if q_client.collection_exists(COLLECTION_NAME):
        print(f"🗑️ Removing existing collection: {COLLECTION_NAME}")
        q_client.delete_collection(COLLECTION_NAME)

    q_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print(f"✅ Collection '{COLLECTION_NAME}' created.")

    # 2. Define the Axion Dataset (§1-§7)
    # This maps the "Unstructured" rules to "Structured" metadata
    rules = [
        {"text": "Product descriptor must be 'AI-assisted', never 'AI-powered'.", "meta": {"section": "§2", "fix": "AI-assisted"}},
        {"text": "Banned verb: 'leverage'. Use 'use', 'apply', or 'harness'.", "meta": {"section": "§3", "fix": "use"}},
        {"text": "Banned filler: 'seamlessly'. Replace with 'simply' or remove.", "meta": {"section": "§3", "fix": "simply"}},
        {"text": "Claim Standard: 'Real-time' must be hyphenated and backed by data.", "meta": {"section": "§4", "fix": "Real-time"}},
        {"text": "LinkedIn: 1-2 sentence paragraphs with double white space.", "meta": {"section": "§5", "fix": "Reformat paragraphs"}},
        {"text": "LinkedIn CTA: Use 'See it in action' or 'Book a demo'.", "meta": {"section": "§5", "fix": "Book a demo"}},
        {"text": "Executive Tone: Focus on ROI and outcomes, not features.", "meta": {"section": "§6", "fix": "Outcome-focused"}},
        {"text": "Practitioner Tone: Focus on speed, ease of use, and workflow.", "meta": {"section": "§6", "fix": "Workflow-focused"}}
    ]

    # 3. Vectorize and Upload
    points = []
    for i, rule in enumerate(rules):
        print(f"📡 Vectorizing Rule {i+1}/{len(rules)} ({rule['meta']['section']})...")
        
        # Generate Embeddings using your text-embedding-3-small-beta deployment
        embedding_response = client.embeddings.create(
            input=rule['text'],
            model=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
        )
        vector = embedding_response.data[0].embedding

        # Create the Point structure
        from qdrant_client.models import PointStruct
        points.append(PointStruct(
            id=i,
            vector=vector,
            payload={
                "rule_text": rule['text'],
                "section": rule['meta']['section'],
                "suggested_fix": rule['meta']['fix']
            }
        ))

    # 4. Push to Qdrant
    q_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("\n" + "="*40)
    print("✅ AXION GOVERNANCE BRAIN LOADED SUCCESSFULLY")
    print(f"📊 Total Rules Ingested: {len(rules)}")
    print("="*40)

if __name__ == "__main__":
    try:
        ingest_brand_guidelines()
    except Exception as e:
        print(f"❌ Critical Error during ingestion: {e}")