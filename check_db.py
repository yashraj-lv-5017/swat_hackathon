from qdrant_client import QdrantClient
import os

client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "axion_governance"

# 1. Check if collection exists
if client.collection_exists(COLLECTION_NAME):
    info = client.get_collection(COLLECTION_NAME)
    print(f"✅ Collection found! Points count: {info.points_count}")
else:
    print("❌ Collection DOES NOT EXIST. Run ingest_rules.py first!")