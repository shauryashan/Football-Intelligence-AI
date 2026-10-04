from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "rag" / "chunks.json"
OUTPUT_FILE = PROJECT_ROOT / "rag" / "embeddings.npz"


# --------------------------------------------------
# MODEL
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# LOAD CHUNKS
# --------------------------------------------------

def load_chunks():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    return chunks


# --------------------------------------------------
# CREATE EMBEDDINGS
# --------------------------------------------------

def create_embeddings(chunks, model):

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"Creating embeddings for {len(texts)} chunks..."
    )

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings


# --------------------------------------------------
# SAVE EMBEDDINGS
# --------------------------------------------------

def save_embeddings(chunks, embeddings):

    chunk_ids = np.array(
        [chunk["chunk_id"] for chunk in chunks],
        dtype=np.int64
    )

    np.savez_compressed(
        OUTPUT_FILE,
        chunk_ids=chunk_ids,
        embeddings=embeddings
    )


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_embeddings(chunks, embeddings):

    print("\n--- EMBEDDING VALIDATION ---")

    expected_chunks = len(chunks)

    actual_embeddings = embeddings.shape[0]

    dimensions = embeddings.shape[1]

    print(
        f"Expected chunks: {expected_chunks}"
    )

    print(
        f"Embedding rows: {actual_embeddings}"
    )

    print(
        f"Embedding dimensions: {dimensions}"
    )

    print(
        f"Data type: {embeddings.dtype}"
    )

    # Check row count
    assert actual_embeddings == expected_chunks

    # Check expected model dimension
    assert dimensions == 384

    # Check for NaN values
    nan_count = np.isnan(embeddings).sum()

    print(
        f"NaN values: {nan_count}"
    )

    assert nan_count == 0

    # Check for infinite values
    infinite_count = np.isinf(embeddings).sum()

    print(
        f"Infinite values: {infinite_count}"
    )

    assert infinite_count == 0

    # Check chunk IDs
    chunk_ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    duplicate_ids = (
        len(chunk_ids)
        - len(set(chunk_ids))
    )

    print(
        f"Duplicate chunk IDs: {duplicate_ids}"
    )

    assert duplicate_ids == 0

    print(
        "\nEMBEDDING VALIDATION: PASSED"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("Loading chunks...")

    chunks = load_chunks()

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    print(
        "\nLoading embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded."
    )

    embeddings = create_embeddings(
        chunks,
        model
    )

    validate_embeddings(
        chunks,
        embeddings
    )

    save_embeddings(
        chunks,
        embeddings
    )

    print(
        f"\nSaved embeddings to:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()