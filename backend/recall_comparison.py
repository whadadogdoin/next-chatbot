import os
from ingest import jina_embed
import json
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient
from vecx.vectorx import VectorX
from pinecone import Pinecone
from beir import util, LoggingHandler, util
from beir.datasets.data_loader import GenericDataLoader
import pandas as pd
from collections import defaultdict
from qdrant_client.models import SearchParams
import time


load_dotenv()

# result = list(embed_queries())

train_qrels =  pd.read_csv("beir_dataset/scifact/qrels/train.tsv", sep='\t', names=["query-id", "corpus-id", "score"])
test_qrels =  pd.read_csv("beir_dataset/scifact/qrels/test.tsv", sep='\t', names=["query-id", "corpus-id", "score"])

combined_qrels = pd.concat([train_qrels,test_qrels], ignore_index=True)
relevant_docs = defaultdict(set)

for _, row in combined_qrels.iterrows():
    relevant_docs[row["query-id"]].add(row["corpus-id"])


def qdrant_recall():

    start = time.time()

    qdrant = QdrantClient(
        api_key=os.getenv("QDRANT_API_KEY"),
        url=os.getenv("QDRANT_URL")
    )

    with open("embedded_queries.json", "r", encoding="utf-8") as f:
        queries = json.load(f)
        total = 0
        num_q = 0
        for query in queries:
            hits = 0
            qid = query.get("id")
            qv = query.get("vector")
            results = qdrant.search(
                collection_name="beir_comp",
                query_vector= qv,
                limit=10,
                search_params=SearchParams(hnsw_ef=128),
            )
            retrieved_ids = set({r.payload.get("source_id") for r in results})
            ground_truth = relevant_docs[qid]
            matched = retrieved_ids & ground_truth
            recall = len(matched)/len(ground_truth)
            total += recall
            num_q +=1
            print(f"Recall for {qid}: {recall}")
        end = time.time()
        print(f"Avg recall Qdrant: {total/num_q:.2f}")
        print(f"Time taken: {end-start:.2f}")

def vectorx_recall():

    start = time.time()

    vx = VectorX(os.getenv("VECX_TOKEN"))
    index = vx.get_index("beir_comp1")

    with open("embedded_queries.json", "r", encoding="utf-8") as f:
        queries = json.load(f)
        total = 0
        num_q = 0
        for query in queries:
            hits = 0
            qid = query.get("id")
            qv = query.get("vector")
            results = index.query(
                vector = qv,
                top_k = 10
            )
            retrieved_ids = set({r["id"] for r in results})
            ground_truth = relevant_docs[qid]
            matched = retrieved_ids & ground_truth
            # print(retrieved_ids)
            # print(ground_truth)
            # print(matched)
            recall = len(matched)/len(ground_truth)
            total += recall
            num_q +=1
            print(f"Recall for {qid}: {recall}")
        end = time.time()
        print(f"Avg recall VectorX: {total/num_q:.2f}")
        print(f"Time taken: {end-start:.2f}")


def pinecone_recall():

    start = time.time()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "beir-comp"

    index = pc.Index(index_name)

    with open("embedded_queries.json", "r", encoding="utf-8") as f:
        queries = json.load(f)
        total = 0
        num_q = 0
        for query in queries:
            hits = 0
            qid = query.get("id")
            qv = query.get("vector")
            results = index.query(
                vector = qv,
                top_k = 10
            )
            retrieved_ids = set({r["id"] for r in results["matches"]})
            ground_truth = relevant_docs[qid]
            matched = retrieved_ids & ground_truth
            recall = len(matched)/len(ground_truth)
            total += recall
            num_q +=1
            print(f"Recall for {qid}: {recall}")
        end = time.time()
        print(f"Avg recall Pinecone: {total/num_q:.2f}")
        print(f"Time taken: {end-start:.2f}")

if __name__=="__main__":
    qdrant_recall()
    vectorx_recall()
    pinecone_recall()