from fastapi import FastAPI
from dotenv import load_dotenv
from google import genai
import os
from vecx.vectorx import VectorX
from ingest import jina_embed
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

vx = VectorX(os.getenv("VECX_TOKEN"))
index = vx.get_index("new_next_index")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chat/{query}")
async def test(query):
    try:
        queryVector=jina_embed([query])[0]

        results = index.query(
            vector=queryVector,
            top_k=10
        )
        passages = [hit['meta']['text'] for hit in results]
        if not passages:
            return {"status": 400, "message": "No result from db"}
        context = "\n\n".join(passages)
        prompt = f"Use the following context to answer the question.\n\n Context:\n {context}\n\n Question: {query}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a chatbot made to help developers learn about the working of Next.js. Send the response text strictly in a mardkdown file."
            ),
            contents=prompt
        )
        return {"status": 200, "result": response}
    except Exception as e:
        print(f"Error while querying: {e}")

