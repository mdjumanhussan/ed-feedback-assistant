# build_db.py
# Step 4: store all 200 comments in a Chroma vector database.
# You only run this once. It saves the database in a folder called "chroma_db".
# Run it with:  python build_db.py

import csv
import chromadb
from chromadb.utils import embedding_functions

# 1. Load the 200 comments from step 2.
with open("ed_feedback.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# 2. Open (or create) the database. It lives in the folder "chroma_db".
client = chromadb.PersistentClient(path="chroma_db")

# 3. Start fresh, so running this twice never makes duplicates.
try:
    client.delete_collection("ed_feedback")
except Exception:
    pass  # nothing to delete the first time

# 4. A "collection" is like a table. We tell it which embedding model to use:
#    the same free model from step 3.
collection = client.create_collection(
    name="ed_feedback",
    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"},  # measure closeness the same way as step 3
)

# 5. Add every comment. Chroma turns each one into numbers and saves it.
#    We also save the theme, sentiment and date, so we can filter by them later.
collection.add(
    ids=[row["id"] for row in rows],
    documents=[row["comment"] for row in rows],
    metadatas=[{"theme": row["theme"], "sentiment": row["sentiment"], "date": row["date"]} for row in rows],
)

print(f"Saved {collection.count()} comments in the database folder 'chroma_db'.")
print("Now run:  python search.py")
