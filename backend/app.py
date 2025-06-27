from fastapi import FastAPI
from dotenv import load_dotenv
from google import genai
import os
from vecx.vectorx import VectorX
from ingest import jina_embed
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

vx = VectorX(os.getenv("VECX_TOKEN"))
index = vx.get_index("next_comp3")

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
            top_k=20
        )
        passages = [hit['meta']['text'] for hit in results]
        if not passages:
            return {"status": 400, "message": "No result from db"}
        context = "\n\n".join(passages)
        prompt = f"""
                    CONTEXT:
                    {context}

                    TASK:
                    Write a **documentation guide** on **{query}** in Next.js:
                    - Give a brief introduction.
                    - Show at least two code snippets.
                    - Use markdown headings, lists, and fenced code blocks.
                    - Do NOT reference or cite the CONTEXT label—just the polished docs.
                    """
        def res_stream():
            response =  client.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="""
                        You are Next.js DocsBot, an expert technical writer. 
                        Always write in a clear, concise documentation style. 
                        Do NOT mention the ingestion context or say “based on provided context.”
                        Use markdown headings, bullet lists, and fenced code blocks.
                        """
                ),
                contents=prompt
            )
            for chunk in response:
                yield chunk.text

        return StreamingResponse(
            res_stream(),
            media_type="text/markdown; charset=utf-8"
        )
    except Exception as e:
        print(f"Error while querying: {e}")

