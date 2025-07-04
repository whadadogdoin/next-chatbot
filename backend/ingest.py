import os
from dotenv import load_dotenv
import requests
import json
from vecx.vectorx import VectorX

load_dotenv()

jina_key = os.getenv("JINA_API_KEY")

API_URL = "https://api.jina.ai/v1/embeddings"

def jina_embed(texts, batch_size=64):
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {jina_key}'
    }
    embeddings = []
    print(f"Length: {len(texts)}")
    total = 0
    for i in range(0,len(texts),batch_size):
        batch = texts[i:i+batch_size]
        # print(batch)
        for att in range(3):
            try:
                data = {
                    "model": "jina-clip-v2",
                    "input": [{"text":t} for t in batch]
                }
                response = requests.post(API_URL,headers=headers, json=data, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"Jina API error: {response.status_code} {response.text}")
                json_response = response.json()
                batch_embeddings = [item["embedding"] for item in json_response.get("data", [])]
                embeddings.extend(batch_embeddings)
                total+=1
                print(f"Embedded {i} to {i+batch_size}")
                break
            except Exception as e:
                att+=1
                print(f"Error while embedding, {i}")
    return embeddings

def main():

    passages = []

    with open("next-js-docs.jsonl","r",encoding="utf-8") as f:
        for line in f:
            step = 250
            size = 500
            obj = json.loads(line)
            text = obj.get("content")
            for i in range(0,max(len(text)-size +1,1),step):
                chunk = text[i:i+step]
                passages.append({"id": f"{obj.get("url")}_{i}", "text": chunk})
    
    texts = [p["text"] for p in passages]
    vectors = jina_embed(texts)

    vx = VectorX(os.getenv("VECX_TOKEN"))
    index = vx.get_index("next_comp3")

    for v,p in zip(vectors,passages):
        # print(v, p["text"])
        index.upsert([{
            "id": p["id"],
            "vector": v,
            "meta": {"text": p["text"]}
        }])
        print(f"upserted {p["id"]}")


    
if __name__ == "__main__":
    main()

    

    


