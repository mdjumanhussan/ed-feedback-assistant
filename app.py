# app.py
# The web page for your ED Feedback Assistant.
# Run it with:  python -m streamlit run app.py
# It opens in your browser. Press Ctrl + C in the terminal to stop it.

import csv
import os

import anthropic
import chromadb
import streamlit as st
from chromadb.utils import embedding_functions

MODEL = "claude-haiku-4-5"
MIN_SCORE = 0.35          # safety check 1: skip weak matches
MAX_QUESTIONS = 10        # per visitor, so a public demo can't use up your credit

RULES = """You help a hospital team understand emergency department patient feedback.
Answer the question using ONLY the numbered patient comments provided.
- Mention the comment numbers you used, like [2] or [1][4].
- If the comments do not answer the question, say:
  "The feedback does not contain enough information to answer this." Do not guess.
- Note whether the comments are mostly positive, mostly negative, or mixed.
- Keep the answer short: 3 to 5 sentences, plain English."""

st.set_page_config(page_title="ED Feedback Assistant", page_icon="🏥")


# ---------- Setup (runs once, then Streamlit remembers it) ----------

@st.cache_resource(show_spinner="Loading the feedback database...")
def get_collection():
    """Open the Chroma database. If it doesn't exist yet (for example on a new
    server), build it from ed_feedback.csv first."""
    client = chromadb.PersistentClient(path="chroma_db")
    embed = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name="ed_feedback", embedding_function=embed, metadata={"hnsw:space": "cosine"}
    )
    if collection.count() == 0:
        with open("ed_feedback.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        collection.add(
            ids=[r["id"] for r in rows],
            documents=[r["comment"] for r in rows],
            metadatas=[{"theme": r["theme"], "sentiment": r["sentiment"], "date": r["date"]} for r in rows],
        )
    return collection


def get_api_key():
    """On your PC the key comes from Windows. Online it comes from Streamlit's secret settings."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        try:
            key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            key = None
    return key


@st.cache_resource
def get_claude(key):
    return anthropic.Anthropic(api_key=key)


# ---------- The page ----------

st.title("🏥 ED Feedback Assistant")
st.caption("Ask a question about emergency department patient feedback. "
           "Demo data: 200 synthetic comments. No real patient data is used.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. **Retrieve:** your question is turned into numbers (an embedding), "
        "and the 5 closest comments are found in a Chroma vector database.\n"
        "2. **Augment:** those comments are given to the AI with strict rules.\n"
        "3. **Generate:** Claude writes a short answer, citing the comments it used.\n\n"
        "**Safety:** weak matches are blocked, and the AI is told to say "
        "*not enough information* rather than guess."
    )
    mood = st.radio("Search which comments?", ["All", "Negative only", "Positive only"])
    st.divider()
    st.caption("Built by Md Juman Hussan · Python, Chroma, Claude, Streamlit")

key = get_api_key()
if not key:
    st.error("No API key found. On your PC, set ANTHROPIC_API_KEY. Online, add it in the app's Secrets.")
    st.stop()

collection = get_collection()
claude = get_claude(key)

if "asked" not in st.session_state:
    st.session_state.asked = 0

st.write("**Try one:**")
examples = ["How do patients feel about waiting times?", "What do patients say about pain relief?", "Was the food good?"]
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        st.session_state.question = ex

question = st.text_input("Your question", key="question", placeholder="e.g. Were staff kind to elderly patients?")

if question:
    if st.session_state.asked >= MAX_QUESTIONS:
        st.warning(f"This demo allows {MAX_QUESTIONS} questions per visit. Refresh the page later to ask more.")
        st.stop()

    where = {"Negative only": {"sentiment": "negative"}, "Positive only": {"sentiment": "positive"}}.get(mood)

    # R: retrieve
    found = collection.query(query_texts=[question], n_results=5, where=where)
    comments = found["documents"][0]
    metas = found["metadatas"][0]
    scores = [1 - d for d in found["distances"][0]]

    if not comments or scores[0] < MIN_SCORE:
        best = f"{scores[0]:.2f}" if comments else "none"
        st.info(f"No comments closely match this question (best score {best}). "
                "The feedback does not seem to cover this topic.")
    else:
        # A + G: give the comments to Claude and get an answer
        numbered = "\n".join(f"[{i}] ({m['sentiment']}) {c}"
                             for i, (c, m) in enumerate(zip(comments, metas), start=1))
        with st.spinner("Claude is reading the comments..."):
            reply = claude.messages.create(
                model=MODEL,
                max_tokens=400,
                system=RULES,
                messages=[{"role": "user", "content": f"Patient comments:\n{numbered}\n\nQuestion: {question}"}],
            )
        st.session_state.asked += 1

        st.subheader("Answer")
        st.write(reply.content[0].text)

        st.subheader("Based on these comments")
        for i, (c, m, s) in enumerate(zip(comments, metas, scores), start=1):
            icon = "🔴" if m["sentiment"] == "negative" else "🟢"
            st.markdown(f"**[{i}]** {icon} *{m['theme']}* · score {s:.2f}  \n{c}")
