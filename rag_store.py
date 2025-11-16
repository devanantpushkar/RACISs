import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
import uuid


EMBED_MODEL = "text-embedding-004"


def get_or_create_index(pc: Pinecone, name: str):
    existing = [idx["name"] for idx in pc.list_indexes()]
    if name not in existing:
        pc.create_index(
            name=name,
            dimension=3072,  # Gemini text-embedding-004
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(name)


def chunk_text(text: str, max_chars: int = 1200):
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks


def embed_single(text: str) -> list[float]:
    resp = genai.embed_content(model=EMBED_MODEL, content=text, task_type="RETRIEVAL_DOCUMENT")
    return resp["embedding"]


def upsert_role_docs(pc: Pinecone, index_name: str, role: str, content_blocks: list[str]):
    index = get_or_create_index(pc, index_name)
    vectors = []
    for text in content_blocks:
        vec = embed_single(text)
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": vec,
            "metadata": {"role": role, "text": text},
        })
    if vectors:
        index.upsert(vectors=vectors)




