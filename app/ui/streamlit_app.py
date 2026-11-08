import streamlit as st

from app.retrieval.generator import Generator
from app.retrieval.retriever import Retriever


st.set_page_config(
    page_title="Local RAG",
    layout="wide",
)

st.title("📄 Local RAG System")

question = st.text_input("Ask a question")

if st.button("Search"):
    if question:
        try:
            chunks = Retriever().retrieve(question)

            if not chunks:
                st.info("No indexed content was found. Run the ingestion command first.")
            else:
                answer = Generator().generate(question, chunks)

                st.markdown("## Answer")
                st.write(answer)

                with st.expander("Retrieved Chunks"):
                    for chunk in chunks:
                        st.write(chunk["content"])
        except Exception:
            st.error(
                "Unable to answer the question. Check that PostgreSQL and "
                "Ollama are running, then try again."
            )
