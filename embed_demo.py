# embed_demo.py
# Step 3: turn each patient comment into numbers (an "embedding"),
# then use those numbers to find the comments closest to a question.
# Run it with:  python embed_demo.py

import csv
import numpy as np
from chromadb.utils import embedding_functions

# 1. Load the 200 comments you made in step 2.
with open("ed_feedback.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
comments = [row["comment"] for row in rows]
print(f"Loaded {len(comments)} comments.")

# 2. Get the embedding model. It is small and free, and it runs on your own PC.
#    The first run downloads it (about 80 MB). After that it is instant.
print("Getting the embedding model. The first run takes a minute or two...")
embed = embedding_functions.DefaultEmbeddingFunction()

# 3. Turn every comment into a list of numbers.
vectors = np.array(embed(comments))
print(f"Done. Each comment is now a list of {vectors.shape[1]} numbers.")

# 4. Look at one, so you can see what an embedding really is.
print()
print("Comment 1:", comments[0])
print("Its first 8 numbers:", np.round(vectors[0][:8], 3))

# 5. Ask a question. Turn the question into numbers the same way.
question = "Was it hard to find a car space?"
question_vector = np.array(embed([question]))[0]

# 6. Score every comment: how close is its meaning to the question?
#    This score is called cosine similarity. Closer to 1 means closer in meaning.
scores = vectors @ question_vector / (
    np.linalg.norm(vectors, axis=1) * np.linalg.norm(question_vector)
)
order = np.argsort(scores)[::-1]   # best score first

print()
print("Question:", question)
print()
print("The 3 closest comments:")
for i in order[:3]:
    print(f"  score {scores[i]:.2f}  [{rows[i]['theme']}]  {comments[i]}")

print()
print("The least related comment:")
i = order[-1]
print(f"  score {scores[i]:.2f}  [{rows[i]['theme']}]  {comments[i]}")
