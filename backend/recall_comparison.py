import os
from ingest import jina_embed
import json
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient
from vecx.vectorx import VectorX

load_dotenv()

embedded_queries = []
expected_result = []

def normalize(text):
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def embed_queries():
    
    path = Path("eval_query.json")

    with path.open("r",encoding="utf-8") as f:
        queries = json.load(f)
        for data in queries:
            query = data.get("query")
            expected = data.get("expected_contains")
            query_vector = jina_embed([query])[0]
            embedded_queries.append(query_vector)
            expected_result.append(expected)
    return zip(embedded_queries,expected_result)

result = list(embed_queries())

def qdrant_recall():

    hits=0

    qdrant = QdrantClient(
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_URL")
    )

    i=0

    for v,ex in result:
        i+=1
        try:
            results = qdrant.search(
                collection_name="next_docs_comp",
                query_vector=v,
                limit=20
            )
            ex_norm = normalize(ex)
            for r in results:
                text_norm = normalize(r.payload.get("text", ""))
                # print(f"{ex_norm}, {text_norm}")
                if ex_norm in text_norm:
                    hits += 1
                    break
            print(f"Successfully queried: {i}. hits: {hits}. Recall rate {hits/i:.2f} in Qdrant")
        except Exception as e:
            print(f"Error while querying: {id}.Error: {e}")

def vectorx_recall():
    hits = 0

    vx = VectorX(os.getenv("VECX_TOKEN"))
    # encryption_key = "160f9e8ca0eba4a7f8225713ed17cf54"
    # encryption_key= "d432adf3b92089b7b63c4f9474301686"
    index = vx.get_index("next_comp3")

    i=0

    # print(result)

    for v,ex in result:
        print("here")
        i+=1
        try:
            results = index.query(
                    vector=v,
                    top_k=20
            )
            ex_norm = normalize(ex)
            for r in results:
                text_norm = normalize(r["meta"]["text"])
                # print(f"{ex_norm}, {text_norm}")
                if ex_norm in text_norm:
                    hits += 1
                    break
            print(f"Successfully queried: {i}. hits: {hits}. Recall rate {hits/i:.2f} in VectorX")
        except Exception as e:
            print(f"Error while querying: {id}.Error: {e}")

if __name__=="__main__":
    qdrant_recall()
    vectorx_recall()

            
# 15 44 46 48 50
# 15 34 44 46 47 50