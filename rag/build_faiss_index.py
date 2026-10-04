from pathlib import Path

import numpy as np
import faiss


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_FILE = PROJECT_ROOT / "rag" / "embeddings.npz"
INDEX_FILE = PROJECT_ROOT / "rag" / "faiss.index"


# -----------------------------
# Load embeddings
# -----------------------------

data = np.load(EMBEDDINGS_FILE)

embeddings = data["embeddings"].astype("float32")

print("Loaded embeddings:")
print("Shape:", embeddings.shape)
print("Dtype:", embeddings.dtype)


# -----------------------------
# Validate embeddings
# -----------------------------

assert embeddings.shape[0] == 151
assert embeddings.shape[1] == 384

assert not np.isnan(embeddings).any()
assert not np.isinf(embeddings).any()

print("\nEmbedding validation: PASSED")


# -----------------------------
# Normalize vectors
# -----------------------------

embeddings_normalized = embeddings.copy()

faiss.normalize_L2(embeddings_normalized)


# -----------------------------
# Build FAISS index
# -----------------------------

dimension = embeddings_normalized.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings_normalized)


# -----------------------------
# Validate index
# -----------------------------

print("\nFAISS index created")
print("Dimension:", index.d)
print("Vectors:", index.ntotal)

assert index.ntotal == 151
assert index.d == 384

print("FAISS index validation: PASSED")


# -----------------------------
# Save index
# -----------------------------

faiss.write_index(index, str(INDEX_FILE))

print("\nSaved FAISS index to:")
print(INDEX_FILE)