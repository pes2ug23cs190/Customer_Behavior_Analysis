"""
Build the RAG knowledge base for the Retail Insights Assistant.
--------------------------------------------------------------
Reads the project's own analysis (README.md + RFM segment summary),
splits it into meaningful chunks, embeds each chunk with a free local
sentence-transformer model, and stores the vectors in a local Chroma
database for retrieval at query time.

Run this once (or whenever README.md / the RFM summary changes):
    python build_index.py
"""

import csv
import re

import chromadb
from sentence_transformers import SentenceTransformer

README_PATH = "README.md"
RFM_SUMMARY_PATH = "rfm/rfm_segment_summary.csv"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "retail_insights"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


def chunk_readme(path: str) -> list[dict]:
    """Split README.md into one chunk per top-level (##) section."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Split on level-2 markdown headers ("## Something"), keeping the header
    # with its content so each chunk is self-contained and citable.
    parts = re.split(r"(?m)^## ", text)
    chunks = []
    for part in parts[1:]:  # parts[0] is the title/badges before the first "##"
        lines = part.strip().splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        # Skip purely structural sections with little retrievable content.
        # (Titles carry emoji prefixes, e.g. "📖 Table of Contents", so this
        # checks substring containment rather than an exact match.)
        if "table of contents" in title.lower():
            continue
        chunks.append(
            {
                "id": f"readme::{title}",
                "text": f"{title}\n{body}",
                "source": f"README.md — {title}",
            }
        )
    return chunks


def chunk_rfm_summary(path: str) -> list[dict]:
    """Turn the RFM segment summary CSV into one readable chunk per segment."""
    chunks = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segment = row.get("segment", "Unknown segment")
            text = (
                f"RFM Segment: {segment}\n"
                f"Number of customers: {row.get('customers')}\n"
                f"Percent of all customers: {row.get('pct_of_customers')}%\n"
                f"Percent of total revenue: {row.get('pct_of_revenue_proxy')}%\n"
                f"Average purchase amount: ${row.get('avg_purchase_amount')}\n"
                f"Average previous purchases: {row.get('avg_previous_purchases')}\n"
                f"Total revenue contribution: ${row.get('total_revenue_proxy')}"
            )
            chunks.append(
                {
                    "id": f"rfm::{segment}",
                    "text": text,
                    "source": f"RFM Segment Summary — {segment}",
                }
            )
    return chunks


def main():
    print("Loading chunks from README.md and RFM summary...")
    chunks = chunk_readme(README_PATH) + chunk_rfm_summary(RFM_SUMMARY_PATH)
    print(f"  -> {len(chunks)} chunks")
    for c in chunks:
        print(f"     - {c['source']}")

    print(f"\nLoading embedding model '{EMBED_MODEL_NAME}' (first run downloads it)...")
    model = SentenceTransformer(EMBED_MODEL_NAME)

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    print(f"Writing to Chroma at ./{CHROMA_DIR} ...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    # Fresh build each run so stale chunks never linger.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )

    print(f"\nDone. Indexed {len(chunks)} chunks into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
