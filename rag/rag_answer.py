from pathlib import Path
import re
import faiss
import json
from sentence_transformers import SentenceTransformer
from openai import OpenAI


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_FILE = PROJECT_ROOT / "rag" / "faiss.index"
CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "qwen3:8b"


# ============================================================
# LOAD FAISS INDEX
# ============================================================

index = faiss.read_index(str(INDEX_FILE))

print("Loaded FAISS index:")
print("Dimension:", index.d)
print("Vectors:", index.ntotal)


# ============================================================
# LOAD CHUNK METADATA
# ============================================================

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print("Loaded chunks:", len(chunks))

assert index.ntotal == len(chunks)

print("FAISS/chunk alignment: PASSED")


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(EMBEDDING_MODEL)


# ============================================================
# OPENAI / OLLAMA CLIENT
# ============================================================

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for keyword matching.
    """

    text = text.lower()

    # Replace punctuation with spaces
    text = re.sub(r"[^a-z0-9%/]+", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(query):
    """
    Extract meaningful keywords from the query.

    Keeps football/project terminology such as:
    attacking midfielder
    scouting score
    role aware
    chance creation
    shooting
    passing
    etc.
    """

    normalized = normalize_text(query)

    stopwords = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "how",
        "what",
        "why",
        "when",
        "where",
        "who",
        "does",
        "do",
        "did",
        "can",
        "could",
        "would",
        "should",
        "this",
        "that",
        "these",
        "those",
        "project",
        "projects",
        "players",
        "player",
        "using",
        "use",
        "used",
        "for",
        "with",
        "from",
        "into",
        "their",
        "his",
        "her",
        "its",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "by",
        "about",
        "through",
        "within",
        "under",
        "role",
        "roles"
    }

    words = normalized.split()

    keywords = [
        word
        for word in words
        if word not in stopwords and len(word) > 2
    ]

    return keywords


# ============================================================
# IMPORTANT PHRASES
# ============================================================

ROLE_PHRASES = [
    "goalkeeper",
    "centre back",
    "center back",
    "full back",
    "fullback",
    "defensive midfielder",
    "central midfielder",
    "attacking midfielder",
    "winger",
    "forward"
]

METHODOLOGY_PHRASES = [
    "scouting score",
    "role aware scouting score",
    "role-aware scouting score",
    "player similarity",
    "role aware similarity",
    "role-aware similarity",
    "scouting profiles",
    "analytical role groups",
    "player ranking",
    "player profiles"
]


# ============================================================
# KEYWORD SCORING
# ============================================================

def calculate_keyword_score(query, chunk):
    """
    Calculate a simple keyword relevance score.

    Exact section/phrase matches receive a strong boost.
    """

    query_normalized = normalize_text(query)

    section = normalize_text(
        chunk.get("section", "")
    )

    text = normalize_text(
        chunk.get("text", "")
    )

    source_text = section + " " + text

    keywords = extract_keywords(query)

    score = 0.0
    matched_keywords = []

    # --------------------------------------------------------
    # Individual keyword matches
    # --------------------------------------------------------

    for keyword in keywords:

        if keyword in source_text:

            score += 1.0
            matched_keywords.append(keyword)

    # --------------------------------------------------------
    # Exact role phrase matches
    # --------------------------------------------------------

    for phrase in ROLE_PHRASES:

        phrase_normalized = normalize_text(phrase)

        if phrase_normalized in query_normalized:

            if phrase_normalized in section:
                score += 3.0

            elif phrase_normalized in text:
                score += 2.0

    # --------------------------------------------------------
    # Exact methodology phrase matches
    # --------------------------------------------------------

    for phrase in METHODOLOGY_PHRASES:

        phrase_normalized = normalize_text(phrase)

        if phrase_normalized in query_normalized:

            if phrase_normalized in section:
                score += 3.0

            elif phrase_normalized in text:
                score += 2.0

    # --------------------------------------------------------
    # Exact section match
    # --------------------------------------------------------

    if section and section == query_normalized:
        score += 5.0

    return score, matched_keywords


# ============================================================
# HYBRID RETRIEVAL
# ============================================================

def retrieve_context(query, top_k=8, semantic_k=30):
    """
    Hybrid retrieval:

    1. FAISS semantic similarity
    2. Keyword matching
    3. Exact role / methodology phrase matching

    The final ranking combines semantic and keyword relevance.
    """

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    # Retrieve a larger candidate pool first.
    search_k = min(
        semantic_k,
        index.ntotal
    )

    scores, indices = index.search(
        query_embedding,
        search_k
    )

    candidates = []

    # --------------------------------------------------------
    # Score candidates
    # --------------------------------------------------------

    for score, index_id in zip(scores[0], indices[0]):

        if index_id < 0 or index_id >= len(chunks):
            continue

        chunk = chunks[index_id]

        semantic_score = float(score)

        keyword_score, matched_keywords = calculate_keyword_score(
            query,
            chunk
        )

        # ----------------------------------------------------
        # Hybrid score
        #
        # Semantic similarity remains important.
        # Keyword matches provide strong boosts for exact
        # project terminology and role sections.
        # ----------------------------------------------------

        hybrid_score = semantic_score + (
            0.40 * keyword_score
        )

        candidates.append({
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "section": chunk["section"],
            "chunk_number": chunk["chunk_number"],
            "similarity": semantic_score,
            "keyword_score": keyword_score,
            "hybrid_score": hybrid_score,
            "matched_keywords": matched_keywords,
            "text": chunk["text"]
        })

    # --------------------------------------------------------
    # Sort by hybrid score
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Return top results
    # --------------------------------------------------------

    results = candidates[:top_k]

    # --------------------------------------------------------
    # Label retrieval type
    # --------------------------------------------------------

    for result in results:

        if result["keyword_score"] > 0:
            result["retrieval_type"] = "hybrid"
        else:
            result["retrieval_type"] = "semantic"

    return results


# ============================================================
# BUILD GROUNDED CONTEXT
# ============================================================

def build_context(results):

    context_parts = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {i}
File: {result["source"]}
Section: {result["section"]}

{result["text"]}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# GENERATE RAG ANSWER
# ============================================================

def answer_question(query, top_k=8):

    results = retrieve_context(
        query,
        top_k=top_k
    )

    context = build_context(results)

    system_prompt = """
You are the Football Intelligence AI project assistant.

Your task is to answer questions about THIS PROJECT using ONLY the
retrieved project documentation.

STRICT GROUNDING RULES:

1. Use only information explicitly stated in the retrieved sources.

2. Do not use outside football knowledge.

3. Do not invent facts, metrics, formulas, weights, percentages,
   calculations, definitions, or methodology.

4. If the retrieved documentation explicitly provides a number,
   percentage, formula, category, definition, or rule, reproduce it
   accurately.

5. If something is not explicitly stated in the retrieved sources,
   say that the retrieved project documentation does not specify it.

6. Do not infer missing information.

7. Do not assume that a metric is important simply because it would
   normally be important in football.

8. Do not claim that a category is prioritized unless the retrieved
   documentation explicitly says so.

9. Do not claim that metrics are normalized, averaged, summed,
   weighted, or calculated in a particular way unless the retrieved
   documentation explicitly says so.

10. When exact role-specific weights are present in the sources,
    report those exact weights.

11. Distinguish clearly between:
    - documented project facts
    - documented limitations
    - information the documentation does not specify

12. Preserve the terminology used by the project.

13. Similarity scores from retrieval are retrieval signals only.
    They are NOT evidence for the factual answer.

14. Keep the answer focused on the user's question.

15. Never fill a documentation gap with a plausible assumption.

IMPORTANT:

If the project documentation does not provide enough information,
say so explicitly.

It is better to provide a smaller fully grounded answer than a longer
answer containing unsupported claims.
"""

    user_prompt = f"""
USER QUESTION:

{query}


RETRIEVED PROJECT DOCUMENTATION:

{context}


INSTRUCTIONS:

Answer the user question using ONLY the retrieved project
documentation above.

Do not use outside knowledge.

Do not infer missing information.

If the documentation provides exact role-specific weights,
include them.

If the documentation does not specify an exact formula or another
requested detail, explicitly say that it does not specify it.
"""

    response = client.responses.create(
        model=LLM_MODEL,
        instructions=system_prompt,
        input=user_prompt
    )

    return response.output_text, results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    query = (
        "How does the project's scouting system evaluate players in the Attacking Midfielder role?"
    )

    answer, results = answer_question(
        query,
        top_k=8
    )

    print("\n" + "=" * 60)
    print("RAG ANSWER")
    print("=" * 60)

    print(answer)

    print("\n" + "=" * 60)
    print("RETRIEVED SOURCES")
    print("=" * 60)

    for i, result in enumerate(results, start=1):

        print(
            f"{i}. "
            f"{result['source']} | "
            f"{result['section']} | "
            f"similarity={result['similarity']:.4f} | "
            f"hybrid={result['hybrid_score']:.4f} | "
            f"type={result['retrieval_type']}"
        )

        if result["matched_keywords"]:
            print(
                "   Matched:",
                ", ".join(result["matched_keywords"])
            )

        print()

        print(result["text"])

        print("-" * 60)