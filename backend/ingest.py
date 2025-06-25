import os
from dotenv import load_dotenv
import requests
import json
from vecx.vectorx import VectorX
from create_index import index

load_dotenv()

jina_key = os.getenv("JINA_API_KEY")
enc_key = os.getenv("ENCRYPTION_KEY")

API_URL = "https://api.jina.ai/v1/embeddings"

def jina_embed(texts, batch_size=32):
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {jina_key}'
    }
    embeddings = []
    for i in range(0,len(texts),batch_size):
        batch = texts[i:i+batch_size]
        # print(batch)
        data = {
            "model": "jina-clip-v2",
            "input": [{"text":t} for t in batch]
        }
        response = requests.post(API_URL,headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Jina API error: {response.status_code} {response.text}")    
        json_response = response.json()
        batch_embeddings = [item["embedding"] for item in json_response.get("data", [])]
        embeddings.extend(batch_embeddings)
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

    

    


