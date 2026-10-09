# search.py
# Step 4: ask the database questions. It finds the 5 closest comments.
# Run it with:  python search.py
# Type a question and press Enter. Type q to quit.

import chromadb
from chromadb.utils import embedding_functions

# Open the database you built with build_db.py.
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(
    name="ed_feedback",
    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
)
print(f"Database ready: {collection.count()} comments.")

while True:
    print()
    question = input("Your question (or q to quit): ").strip()
    if question.lower() == "q":
        break
    if not question:
        continue

    # Optional: only look at negative comments, or only positive ones.
    mood = input("Only negative, only positive, or all? (n / p / Enter for all): ").strip().lower()
    where = {"n": {"sentiment": "negative"}, "p": {"sentiment": "positive"}}.get(mood)

    # Ask Chroma for the 5 closest comments.
    results = collection.query(query_texts=[question], n_results=5, where=where)

    print()
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        score = 1 - dist  # turn "distance" into the same score as step 3 (closer to 1 = closer meaning)
        print(f"  score {score:.2f}  [{meta['theme']}, {meta['sentiment']}]  {doc}")
