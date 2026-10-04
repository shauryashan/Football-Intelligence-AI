from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.json"
EMBEDDINGS_FILE = PROJECT_ROOT / "rag" / "embeddings.npz"


# --------------------------------------------------
# MODEL
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# LOAD CHUNKS
# --------------------------------------------------

def load_chunks():

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    return chunks


# --------------------------------------------------
# LOAD EMBEDDINGS
# --------------------------------------------------

def load_embeddings():

    data = np.load(
        EMBEDDINGS_FILE
    )

    chunk_ids = data["chunk_ids"]
    embeddings = data["embeddings"]

    return chunk_ids, embeddings


# --------------------------------------------------
# VALIDATE ALIGNMENT
# --------------------------------------------------

def validate_alignment(
    chunks,
    chunk_ids,
    embeddings
):

    print("\n--- DATA ALIGNMENT VALIDATION ---")

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Embedding rows: {len(chunk_ids)}"
    )

    print(
        f"Embedding dimensions: "
        f"{embeddings.shape[1]}"
    )

    assert len(chunks) == len(chunk_ids)

    assert embeddings.shape[0] == len(chunks)

    for index, chunk in enumerate(chunks):

        assert (
            chunk["chunk_id"]
            == int(chunk_ids[index])
        )

    print(
        "Chunk/embedding alignment: PASSED"
    )


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

def search(
    query,
    model,
    chunks,
    embeddings,
    top_k=5
):

    # Convert the query into an embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Calculate cosine similarity
    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    # Get highest-scoring chunks
    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append(
            {
                "chunk_id": chunks[index]["chunk_id"],
                "source": chunks[index]["source"],
                "section": chunks[index]["section"],
                "chunk_number": chunks[index]["chunk_number"],
                "similarity": float(
                    similarities[index]
                ),
                "text": chunks[index]["text"]
            }
        )

    return results


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

def display_results(
    query,
    results
):

    print("\n" + "=" * 70)

    print(
        f"QUERY: {query}"
    )

    print("=" * 70)

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n--- RESULT {rank} ---"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Section: {result['section']}"
        )

        print(
            f"Chunk: {result['chunk_number']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print("\nText:")

        print(
            result["text"]
        )


# --------------------------------------------------
# SEARCH VALIDATION
# --------------------------------------------------

def validate_search(
    results,
    expected_source,
    expected_section
):

    print("\n--- SEARCH VALIDATION ---")

    print(
        f"Results returned: {len(results)}"
    )

    assert len(results) > 0

    sources = [
        result["source"]
        for result in results
    ]

    sections = [
        result["section"]
        for result in results
    ]

    print(
        f"Expected source: {expected_source}"
    )

    print(
        f"Expected section: {expected_section}"
    )

    print(
        f"Returned sources: {sources}"
    )

    print(
        f"Returned sections: {sections}"
    )

    assert expected_source in sources

    section_match = any(
    expected_section.lower() in section.lower()
    for section in sections
)

    assert section_match

    print(
        "\nSEMANTIC SEARCH VALIDATION: PASSED"
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

    print("\nLoading embeddings...")

    chunk_ids, embeddings = load_embeddings()

    validate_alignment(
        chunks,
        chunk_ids,
        embeddings
    )

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded."
    )

    # --------------------------------------------------
    # TEST QUERY
    # --------------------------------------------------

    query = (
        "How is the role-aware scouting score calculated?"
    )

    results = search(
        query=query,
        model=model,
        chunks=chunks,
        embeddings=embeddings,
        top_k=5
    )

    display_results(
        query,
        results
    )

    validate_search(
        results,
        expected_source="scouting_methodology.md",
        expected_section="Role-Aware Scouting Score"
    )


if __name__ == "__main__":
    main()