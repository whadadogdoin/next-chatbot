import json
from ingest import jina_embed

def embed_query_data():
    print("embedding query")
    embedded_queries = []
    idx = 1
    with open("./beir_dataset/scifact/queries.jsonl","r",encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            query = obj.get("text")
            query_vector = jina_embed([query])[0]
            embedded_queries.append({
                "id": obj.get("_id"),
                "text": obj.get("text"),
                "vector": query_vector  
            })
            print(f"embedded query {idx}: {obj.get("_id")}")
            idx+=1
    with open("embedded_queries.json", "w", encoding="utf-8") as f:
        json.dump(embedded_queries, f, indent=2)
    print("Saved embedded queries file")

embed_query_data()