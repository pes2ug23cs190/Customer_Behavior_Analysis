"""
Retail Insights Assistant -- Streamlit demo UI.
-------------------------------------------------
Run with: streamlit run rag_app.py

Requires:
  1. `python build_index.py` run at least once (creates ./chroma_db)
  2. GEMINI_API_KEY set in a local .env file
"""

import streamlit as st

from query_rag import answer_question

st.set_page_config(page_title="Retail Insights Assistant", page_icon="🛍️")

st.title("🛍️ Retail Insights Assistant")
st.caption(
    "Ask a question about the Customer Shopping Behavior Analysis project. "
    "Answers are grounded in the project's own README and RFM segmentation "
    "results using Retrieval-Augmented Generation (RAG) -- not general "
    "knowledge, so the assistant will say so if something isn't covered."
)

EXAMPLE_QUESTIONS = [
    "Which customer segment should marketing prioritize?",
    "Why was a recency proxy used instead of real recency?",
    "Which products are most dependent on discounts?",
    "What's the capital of France?",  # intentionally out-of-scope, to demo grounding
]

st.write("**Try an example, or ask your own question:**")
cols = st.columns(2)
clicked_question = None
for i, q in enumerate(EXAMPLE_QUESTIONS):
    if cols[i % 2].button(q, use_container_width=True):
        clicked_question = q

question = st.text_input("Your question:", value=clicked_question or "")

if st.button("Ask", type="primary") or clicked_question:
    if not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Retrieving relevant analysis and generating an answer..."):
            try:
                result = answer_question(question)
                st.markdown("### Answer")
                st.write(result["answer"])
                with st.expander("Retrieved sources used for this answer"):
                    for s in result["sources"]:
                        st.write(f"- {s}")
            except RuntimeError as e:
                st.error(str(e))
