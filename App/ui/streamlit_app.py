import streamlit as st

from app.retrieval.generator import Generator
from app.retrieval.retriever import Retriever


retriever = Retriever()

generator = Generator()


st.set_page_config(

    page_title="Local RAG",

    layout="wide"

)

st.title("📄 Local RAG System")

question = st.text_input(

    "Ask a question"

)

if st.button("Search"):

    if question:

        chunks = retriever.retrieve(

            question

        )

        answer = generator.generate(

            question,

            chunks

        )

        st.markdown("## Answer")

        st.write(answer)

        with st.expander(

            "Retrieved Chunks"

        ):

            for chunk in chunks:

                st.write(

                    chunk["content"]

                )