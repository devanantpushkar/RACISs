import google.generativeai as genai
from pinecone import Pinecone


EMBED_MODEL = "text-embedding-004"
GEN_MODEL = "gemini-2.5-flash"


def embed_query(query: str) -> list[float]:
    resp = genai.embed_content(model=EMBED_MODEL, content=query, task_type="RETRIEVAL_QUERY")
    return resp["embedding"]


def retrieve_context(pc: Pinecone, index_name: str, role: str, query: str, top_k: int = 5) -> list[str]:
    index = pc.Index(index_name)
    qvec = embed_query(query)
    res = index.query(
        vector=qvec,
        top_k=top_k,
        include_metadata=True,
        filter={"role": {"$eq": role}},
    )
    matches = res.get("matches", [])
    return [m.get("metadata", {}).get("text", "") for m in matches if m.get("metadata")]


def answer_with_context(query: str, role: str, context_chunks: list[str]) -> str:
    context = "\n\n".join([c for c in context_chunks if c])
    prompt = f"""
Role: {role}
Question: {query}

Context (relevant for this role):
```
{context}
```

Answer concisely for the {role}. If not found in context, say you don't have that info.
"""
    resp = genai.GenerativeModel(GEN_MODEL).generate_content(prompt)
    return resp.text.strip()




