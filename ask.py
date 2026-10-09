# ask.py
# Step 5: the full RAG app.
#   R = Retrieve: find the 5 comments closest to your question (from Chroma)
#   A = Augment:  put those comments into the instructions for the AI
#   G = Generate: the AI writes an answer, using ONLY those comments
# Run it with:  python ask.py
# Type a question and press Enter. Type q to quit.

import anthropic
import chromadb
from chromadb.utils import embedding_functions

MODEL = "claude-haiku-4-5"   # Claude's fastest, cheapest model. Good for this job.
MIN_SCORE = 0.35             # below this, we treat a comment as "not really related"

# The rules we give the AI. This is where we stop it making things up.
RULES = """You help a hospital team understand emergency department patient feedback.
Answer the question using ONLY the numbered patient comments provided.
- Mention the comment numbers you used, like [2] or [1][4].
- If the comments do not answer the question, say:
  "The feedback does not contain enough information to answer this." Do not guess.
- Note whether the comments are mostly positive, mostly negative, or mixed.
- Keep the answer short: 3 to 5 sentences, plain English."""

# Open the database from step 4, and connect to Claude.
db = chromadb.PersistentClient(path="chroma_db")
collection = db.get_collection(
    name="ed_feedback",
    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
)
claude = anthropic.Anthropic()  # reads your key from ANTHROPIC_API_KEY
print(f"ED Feedback Assistant ready. {collection.count()} comments in the database.")

while True:
    print()
    question = input("Your question (or q to quit): ").strip()
    if question.lower() == "q":
        break
    if not question:
        continue

    # R: retrieve the 5 closest comments.
    found = collection.query(query_texts=[question], n_results=5)
    comments = found["documents"][0]
    metas = found["metadatas"][0]
    scores = [1 - d for d in found["distances"][0]]

    # Safety check 1: if even the best match is weak, don't ask the AI at all.
    if scores[0] < MIN_SCORE:
        print(f"\nNo comments closely match this question (best score {scores[0]:.2f}).")
        print("The feedback does not seem to cover this topic.")
        continue

    # A: put the comments into the message, numbered so the AI can cite them.
    numbered = "\n".join(f"[{i}] ({m['sentiment']}) {c}" for i, (c, m) in enumerate(zip(comments, metas), start=1))
    message = f"Patient comments:\n{numbered}\n\nQuestion: {question}"

    # G: ask Claude to write the answer. (Safety check 2 is inside RULES.)
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=400,
        system=RULES,
        messages=[{"role": "user", "content": message}],
    )

    print("\nANSWER:")
    print(reply.content[0].text)
    print("\nBASED ON:")
    for i, (c, m, s) in enumerate(zip(comments, metas, scores), start=1):
        print(f"  [{i}] score {s:.2f}  [{m['theme']}, {m['sentiment']}]  {c}")
