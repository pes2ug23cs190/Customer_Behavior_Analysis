"""
Retail Insights Assistant -- retrieval + generation.
-----------------------------------------------------
Given a natural-language question, retrieves the most relevant chunks
from the project's own analysis (indexed by build_index.py) and asks
Gemini to answer using ONLY that retrieved context, citing its source.

Requires GEMINI_API_KEY in a local .env file (see .env.example).
Run `python build_index.py` once first to create the vector index.
"""

import os

import chromadb
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "retail_insights"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-3.6-flash"
TOP_K = 3

load_dotenv()

_embed_model = None
_collection = None
_genai_client = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        try:
            _collection = client.get_collection(COLLECTION_NAME)
        except Exception as e:
            raise RuntimeError(
                "Vector index not found. Run 'python build_index.py' first."
            ) from e
    return _collection


def _get_genai_client():
    global _genai_client
    if _genai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Add it to your .env file (see .env.example)."
            )
        _genai_client = genai.Client(api_key=api_key)
    return _genai_client


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """Return the top_k most relevant chunks for a question, with sources."""
    model = _get_embed_model()
    collection = _get_collection()

    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "source": meta["source"], "distance": dist})
    return hits


def build_prompt(question: str, hits: list[dict]) -> str:
    context_block = "\n\n".join(
        f"[Source: {h['source']}]\n{h['text']}" for h in hits
    )
    return f"""You are a retail analytics assistant answering questions about a specific customer shopping behavior analysis project.

Rules:
- Answer ONLY using the CONTEXT below. Do not use outside knowledge.
- If the context does not contain enough information to answer, say exactly:
  "This isn't covered in my project analysis."
- When you do answer, end with a line "Source: <source name>" citing which
  context chunk(s) you used, exactly as labeled below.
- Be concise and business-focused, as if briefing a marketing/retention stakeholder.

CONTEXT:
{context_block}

QUESTION:
{question}

ANSWER:"""


def ask_gemini(prompt: str) -> str:
    client = _get_genai_client()
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text


def answer_question(question: str, top_k: int = TOP_K) -> dict:
    """Full RAG pipeline: retrieve -> build prompt -> generate -> return answer + sources."""
    hits = retrieve(question, top_k=top_k)
    prompt = build_prompt(question, hits)
    answer = ask_gemini(prompt)
    return {
        "question": question,
        "answer": answer,
        "sources": [h["source"] for h in hits],
    }


if __name__ == "__main__":
    print("Retail Insights Assistant -- ask a question (or 'quit' to exit)\n")
    while True:
        q = input("You: ").strip()
        if not q or q.lower() in {"quit", "exit"}:
            break
        result = answer_question(q)
        print(f"\nAssistant: {result['answer']}\n")
        print(f"(Retrieved from: {', '.join(result['sources'])})\n")
