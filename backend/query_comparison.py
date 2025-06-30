import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from ingest import jina_embed
import json
import time
from vecx.vectorx import VectorX
from pathlib import Path
from pinecone import Pinecone
import statistics


def qdrant_query():
    start = time.time()

    qdrant = QdrantClient(
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_URL")
    )

    path = Path("queries.json")

    times = []

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                qtime_start = time.time()
                qdrant.search(
                    collection_name="next_docs_comp",
                    query_vector=query_vector,
                    limit=100
                )
                qtime_end = time.time()
                times.append(qtime_end-qtime_start)
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    print("Latency over 50 runs for Qdrant: ")
    print(f"mean:   {statistics.mean(times)*1000:.1f} ms")
    print(f"median: {statistics.median(times)*1000:.1f} ms")
    print(f"p95:    {statistics.quantiles(times, n=100)[94]*1000:.1f} ms")
    print(f"p99:    {statistics.quantiles(times, n=100)[98]*1000:.1f} ms")
    
    end = time.time()

    print(f"Time taken to query Qdrant: {end-start:.4f} seconds")

def vectorx_query():
    start=time.time()

    vx = VectorX(os.getenv("VECX_TOKEN"))
    # encryption_key = "160f9e8ca0eba4a7f8225713ed17cf54"
    # encryption_key= "d432adf3b92089b7b63c4f9474301686"
    # encryption_key="087f90ac527feca98886fbda155a85bc"
    encryption_key = "2ab0e11c34f71e1c4fdb66e16f9e66d0"
    index = vx.get_index("next_enc_comp12",encryption_key)

    times = []

    path = Path("queries.json")

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                qtime_start = time.time()
                index.query(
                    vector=query_vector,
                    top_k=100
                )
                qtime_end = time.time()
                times.append(qtime_end-qtime_start)
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    print("Latency over 50 runs for VectorX: ")
    print(f"mean:   {statistics.mean(times)*1000:.1f} ms")
    print(f"median: {statistics.median(times)*1000:.1f} ms")
    print(f"p95:    {statistics.quantiles(times, n=100)[94]*1000:.1f} ms")
    print(f"p99:    {statistics.quantiles(times, n=100)[98]*1000:.1f} ms")
    
    end = time.time()
    print(f"Time taken to query VectorX: {end-start:.4f} seconds")

def pinecone_query():
    start = time.time()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "next-comp-2"

    index = pc.Index(index_name)

    path = Path("queries.json")

    times = []

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            id = data.get("id")
            query_vector = jina_embed([query])[0]
            try:
                qtime_start = time.time()
                index.query(
                    vector=query_vector,
                    top_k=100,
                    include_metadata=True
                )
                qtime_end = time.time()
                times.append(qtime_end-qtime_start)
                print(f"Successfully queried: {id}")
            except Exception as e:
                print(f"Error while querying: {id}, {query}: {e}")
    print("Latency over 50 runs for VectorX: ")
    print(f"mean:   {statistics.mean(times)*1000:.1f} ms")
    print(f"median: {statistics.median(times)*1000:.1f} ms")
    print(f"p95:    {statistics.quantiles(times, n=100)[94]*1000:.1f} ms")
    print(f"p99:    {statistics.quantiles(times, n=100)[98]*1000:.1f} ms")
    
    end = time.time()
    print(f"Time taken to query Pinecone: {end-start:.4f} seconds")

if __name__=="__main__":
    # qdrant_query()
    vectorx_query()
    # pinecone_query()




