from ingest import jina_embed
from dotenv import load_dotenv
from vecx.vectorx import VectorX
import os

load_dotenv()

def query(param):
    queryVector = jina_embed([param])[0]
    vx = VectorX(os.getenv("VECX_TOKEN"))
    index = vx.get_index("new_next_index")

    results = index.query(
        vector=queryVector,
        top_k=10,
    )

    passages = [hit['meta']['text'] for hit in results]

    print(passages)

query("Next.js routing?")