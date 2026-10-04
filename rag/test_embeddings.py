from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded successfully.")


# --------------------------------------------------
# TEST TEXT
# --------------------------------------------------

texts = [
    "Expected goals estimates the probability that a shot results in a goal.",
    "The project uses StatsBomb shot xG values.",
    "A player can be compared with other players using statistical features."
]


# --------------------------------------------------
# CREATE EMBEDDINGS
# --------------------------------------------------

print("\nCreating embeddings...")

embeddings = model.encode(
    texts,
    convert_to_numpy=True
)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("\n--- EMBEDDING VALIDATION ---")

print(
    f"Number of texts: {len(texts)}"
)

print(
    f"Embedding shape: {embeddings.shape}"
)

print(
    f"Embedding dimensions: {embeddings.shape[1]}"
)

print(
    f"Data type: {embeddings.dtype}"
)

print(
    f"First embedding first 5 values:"
    f"\n{embeddings[0][:5]}"
)


# --------------------------------------------------
# BASIC VALIDATION
# --------------------------------------------------

assert embeddings.shape[0] == len(texts)

assert embeddings.shape[1] > 0

assert embeddings.shape[0] == 3

print("\nEMBEDDING VALIDATION: PASSED")