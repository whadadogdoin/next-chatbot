import json
from ingest import jina_embed
import time
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from hashlib import md5
from vecx.vectorx import VectorX
from pinecone import Pinecone, ServerlessSpec
from pathlib import Path

load_dotenv()

passages = []

def embed_corpus_data():
    print("start embedding")
    with open("beir_dataset/scifact/corpus.jsonl","r", encoding = "utf-8") as f:
        for line in f:
            data = json.loads(line)
            step = 250
            size = 500
            obj = json.loads(line)
            text = obj.get("text")
            for i in range(0,max(len(text)-size +1,1),step):
                chunk = text[i:i+step]
                passages.append({"id": obj.get("_id"), "text": chunk})
    texts = [p["text"] for p in passages]
    vectors = jina_embed(texts)
    return vectors

vectors = embed_corpus_data()

def upsert_qdrant():

    start = time.time()

    qdrant = QdrantClient(
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_URL")
    )

    points = [
        PointStruct(id=int(md5(p["id"].encode()).hexdigest(),16) % (10**12), vector=v, payload = {"text": p["text"], "source_id": p["id"]}) for v,p in zip(vectors,passages)
    ]
    
    qdrant.create_collection(
        collection_name="beir_comp",
        vectors_config={"size": len(points[0].vector), "distance": "Cosine"}
    )

    BATCH_SIZE = 100
    for i in range(0, len(points), BATCH_SIZE):
        batch_points = points[i : i + BATCH_SIZE]
        qdrant.upsert(collection_name="beir_comp", points=batch_points)
        print(f"Upserted points {i} to {i+len(batch_points)}")

    # qdrant.delete_collection("next_docs_comp")
    
    end = time.time()

    print(f"Ingestion Complete in Qdrant. Time taken : {end-start:.4f} seconds")

def upsert_vectorx():
    start = time.time()

    vx = VectorX(os.getenv("VECX_TOKEN"))
    vx.create_index(
        name="beir_comp1",
        dimension=1024,
        space_type="cosine",
    )

    index = vx.get_index("beir_comp1")

    batch_size=100

    for i in range(0,len(vectors),batch_size):
        batch_vectors=vectors[i:i+batch_size]
        batch_passages=passages[i:i+batch_size]
        payload = [
            {
                "id": p["id"],
                "vector": v,
                "meta": {"text": p["text"]}
            } for v,p in zip(batch_vectors,batch_passages)
        ]
        index.upsert(payload)
        print(f"Upserted points {i} to {i+len(batch_vectors)}")

    end = time.time()

    print(f"Ingestion Complete in VectorX. Time taken : {end-start:.4f} seconds")

def upsert_pinecone():
    start = time.time()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "beir-comp"
    
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    index = pc.Index(index_name)

    batch_size=100

    for i in range(0,len(vectors),batch_size):
        batch_vectors=vectors[i:i+batch_size]
        batch_passages=passages[i:i+batch_size]
        payload = [
            {
                "id": p["id"],
                "values": v,
                "metadata": {"text": p["text"]}
            } for v,p in zip(batch_vectors,batch_passages)
        ]
        index.upsert(vectors=payload)
        print(f"Upserted points {i} to {i+len(batch_vectors)}")

    end = time.time()

    print(f"Ingestion Complete in Pinecone. Time taken : {end-start:.4f} seconds")

if __name__=="__main__":
    upsert_qdrant()
    # upsert_vectorx()
    # upsert_pinecone()






