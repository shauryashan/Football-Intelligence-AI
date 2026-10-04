from pathlib import Path

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_FILE = PROJECT_ROOT / "rag" / "faiss.index"
CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.json"

MODEL_NAME = "all-MiniLM-L6-v2"


# -----------------------------
# Load FAISS index
# -----------------------------

index = faiss.read_index(str(INDEX_FILE))

print("Loaded FAISS index:")
print("Dimension:", index.d)
print("Vectors:", index.ntotal)


# -----------------------------
# Load chunk metadata
# -----------------------------

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print("Loaded chunks:", len(chunks))


# -----------------------------
# Validate alignment
# -----------------------------

assert index.ntotal == len(chunks)
assert index.d == 384

print("\nFAISS/chunk alignment: PASSED")


# -----------------------------
# Load embedding model
# -----------------------------

model = SentenceTransformer(MODEL_NAME)


# -----------------------------
# Semantic search
# -----------------------------

def search(query, top_k=5):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    # Normalize query so inner product = cosine similarity
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(scores[0], indices[0]):

        chunk = chunks[index_id]

        results.append({
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "section": chunk["section"],
            "chunk_number": chunk["chunk_number"],
            "similarity": float(score),
            "text": chunk["text"]
        })

    return results


# -----------------------------
# Validation query
# -----------------------------

query = "How is the role-aware scouting score calculated?"

results = search(query, top_k=5)


print("\n--- FAISS SEARCH RESULTS ---")
print("Query:", query)

for i, result in enumerate(results, start=1):

    print(f"\nResult {i}")
    print("Source:", result["source"])
    print("Section:", result["section"])
    print("Chunk:", result["chunk_number"])
    print("Similarity:", round(result["similarity"], 4))
    print("Text:", result["text"][:300])


# -----------------------------
# Retrieval validation
# -----------------------------

expected_source = "scouting_methodology.md"
expected_section = "Role-Aware Scouting Score"

sources = [result["source"] for result in results]
sections = [result["section"] for result in results]

assert expected_source in sources

section_match = any(
    expected_section.lower() in section.lower()
    for section in sections
)

assert section_match

print("\nFAISS retrieval validation: PASSED")