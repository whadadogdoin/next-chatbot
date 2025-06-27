import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from ingest import jina_embed
import json
import time
from vecx.vectorx import VectorX
from pathlib import Path
from pinecone import Pinecone

def qdrant_query():
    start = time.time()

    qdrant = QdrantClient(
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_URL")
    )

    path = Path("queries.json")

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                qdrant.search(
                    collection_name="next_docs_comp",
                    query_vector=query_vector,
                    limit=100
                )
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    
    end = time.time()

    print(f"Time taken to query Qdrant: {end-start:.4f} seconds")

def vectorx_query():
    start=time.time()

    vx = VectorX(os.getenv("VECX_TOKEN"))
    # encryption_key = "160f9e8ca0eba4a7f8225713ed17cf54"
    # encryption_key= "d432adf3b92089b7b63c4f9474301686"
    index = vx.get_index("next_comp3")

    path = Path("queries.json")

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                index.query(
                    vector=query_vector,
                    top_k=100
                )
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    
    end = time.time()
    print(f"Time taken to query VectorX: {end-start:.4f} seconds")

def pinecone_query():
    start = time.time()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "next-comp-2"

    index = pc.Index(index_name)

    path = Path("queries.json")

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                index.query(
                    vector=query_vector,
                    top_k=100,
                    include_metadata=True
                )
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    
    end = time.time()
    print(f"Time taken to query Pinecone: {end-start:.4f} seconds")

if __name__=="__main__":
    # qdrant_query()
    vectorx_query()
    # pinecone_query()




