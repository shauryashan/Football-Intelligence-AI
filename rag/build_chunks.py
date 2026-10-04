from pathlib import Path
import json
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = PROJECT_ROOT / "rag" / "documents"
OUTPUT_FILE = PROJECT_ROOT / "rag" / "chunks.json"

CHUNK_SIZE = 1200
OVERLAP = 200


# --------------------------------------------------
# Split oversized text while preserving overlap
# --------------------------------------------------

def split_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk.strip())

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# --------------------------------------------------
# Parse Markdown sections
# --------------------------------------------------

def parse_sections(text):

    lines = text.splitlines()

    sections = []

    current_heading = "Document Introduction"
    current_content = []

    for line in lines:

        heading_match = re.match(
            r"^(#{1,6})\s+(.+)$",
            line.strip()
        )

        if heading_match:

            if current_content:

                sections.append({
                    "section": current_heading,
                    "text": "\n".join(current_content).strip()
                })

            current_heading = heading_match.group(2).strip()
            current_content = []

        else:

            current_content.append(line)

    if current_content:

        sections.append({
            "section": current_heading,
            "text": "\n".join(current_content).strip()
        })

    return sections


# --------------------------------------------------
# Build chunks
# --------------------------------------------------

all_chunks = []

chunk_id = 0


for document_path in sorted(DOCUMENTS_DIR.glob("*.md")):

    print(f"\nProcessing: {document_path.name}")

    text = document_path.read_text(
        encoding="utf-8"
    )

    sections = parse_sections(text)

    print("Sections:", len(sections))

    document_chunk_number = 0

    for section in sections:

        section_name = section["section"]
        section_text = section["text"]

        if not section_text:
            continue

        # Keep normal sections together.
        if len(section_text) <= CHUNK_SIZE:

            text_chunks = [section_text]

        else:

            text_chunks = split_text(
                section_text
            )

        for text_chunk in text_chunks:

            if not text_chunk:
                continue

            all_chunks.append({
                "chunk_id": chunk_id,
                "source": document_path.name,
                "section": section_name,
                "chunk_number": document_chunk_number,
                "text": f"{section_name}\n\n{text_chunk}"
            })

            chunk_id += 1
            document_chunk_number += 1


# --------------------------------------------------
# Validation
# --------------------------------------------------

print("\n" + "=" * 60)
print("CHUNK VALIDATION")
print("=" * 60)

print("Total chunks:", len(all_chunks))

assert len(all_chunks) > 0

chunk_ids = [
    chunk["chunk_id"]
    for chunk in all_chunks
]

assert len(chunk_ids) == len(set(chunk_ids))

assert all(
    chunk["source"]
    and chunk["section"]
    and chunk["text"]
    for chunk in all_chunks
)

assert all(
    len(chunk["text"]) <= CHUNK_SIZE
    for chunk in all_chunks
)

print("Duplicate chunk IDs: 0")
print("Missing metadata: 0")
print("Oversized chunks: 0")


# --------------------------------------------------
# Source distribution
# --------------------------------------------------

print("\nChunks by source:")

source_counts = {}

for chunk in all_chunks:

    source = chunk["source"]

    source_counts[source] = (
        source_counts.get(source, 0) + 1
    )

for source, count in source_counts.items():

    print(f"{source}: {count}")


# --------------------------------------------------
# Save
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_chunks,
        file,
        indent=2,
        ensure_ascii=False
    )

print("\nSaved chunks to:")
print(OUTPUT_FILE)

print("\nChunking validation: PASSED")