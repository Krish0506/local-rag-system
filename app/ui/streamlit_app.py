import time
from pathlib import Path

import streamlit as st

from app.config.settings import PROJECT_ROOT, settings
from app.health import database_health, knowledge_base_counts, ollama_health
from app.ingestion.parser import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import IngestionPipeline
from app.llm.chat import resolve_model
from app.retrieval.generator import Generator
from app.retrieval.retriever import Retriever
from app.storage.faiss_store import FAISSStore


DEMO_DATA_DIR = PROJECT_ROOT / "demo_data"


def render_sources(sources):
    if not sources:
        st.caption("No source excerpts were returned for this answer.")
        return

    with st.container(border=True):
        st.markdown("**Sources**")
        for index, source in enumerate(sources, start=1):
            filename = source.get("filename") or "Unknown document"
            location = source.get("location")
            excerpt = (source.get("content") or "").strip()

            if excerpt:
                excerpt = excerpt[:240].replace("\n", " ") + "..."

            line = f"**[{index}] {filename}**"
            if location:
                line = f"{line} · {location}"
            if excerpt:
                line = f"{line}  \n{excerpt}"

            st.markdown(line)


def render_ingestion_results(results):
    if not results:
        st.sidebar.warning("No supported files were found.")
        return

    for result in results:
        status = result["status"]
        detail = result["detail"]

        if status == "ingested":
            st.sidebar.success(f"{result['filename']}: ingested")
        elif status == "skipped":
            st.sidebar.info(f"{result['filename']}: already ingested")
        else:
            st.sidebar.error(f"{result['filename']}: {detail or 'ingestion failed'}")


def render_service_status():
    st.sidebar.subheader("Service status")

    if database_health():
        st.sidebar.success("PostgreSQL: connected")
    else:
        st.sidebar.error("PostgreSQL: unavailable")

    if ollama_health():
        st.sidebar.success("Ollama: connected")
    else:
        st.sidebar.error("Ollama: unavailable")

    try:
        document_count, chunk_count = knowledge_base_counts()
        st.sidebar.metric("Documents", document_count)
        st.sidebar.metric("Chunks", chunk_count)
    except Exception:
        st.sidebar.warning("Knowledge base counts unavailable")

    try:
        vector_store = FAISSStore()
        st.sidebar.metric("Vector index", vector_store.index.ntotal)
    except Exception:
        st.sidebar.warning("Vector index unavailable")

    st.sidebar.caption(f"Model: `{resolve_model()}`")
    st.sidebar.caption(f"Embeddings: `{settings.EMBEDDING_MODEL}`")
    st.sidebar.caption("First request may take 10–15 seconds while the model loads.")


def render_ingestion_controls():
    st.sidebar.subheader("Knowledge base")

    if st.sidebar.button("Ingest demo documents"):
        pipeline = IngestionPipeline()
        render_ingestion_results(pipeline.ingest_directory(DEMO_DATA_DIR))

    uploaded_files = st.sidebar.file_uploader(
        "Upload engineering documents",
        type=sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
    )

    if st.sidebar.button("Ingest uploaded files"):
        if not uploaded_files:
            st.sidebar.warning("Select at least one file first.")
        else:
            pipeline = IngestionPipeline()
            target_directory = Path(settings.raw_directory)
            target_directory.mkdir(parents=True, exist_ok=True)
            results = []

            for uploaded_file in uploaded_files:
                extension = Path(uploaded_file.name).suffix.lower()
                target = target_directory / f"{time.strftime('%Y%m%d-%H%M%S')}_{uploaded_file.name}"

                try:
                    target.write_bytes(uploaded_file.getvalue())
                    ingested = pipeline.ingest(target)
                    results.append(
                        {
                            "filename": uploaded_file.name,
                            "status": "ingested" if ingested else "skipped",
                            "detail": "",
                        }
                    )
                except Exception as exc:
                    results.append(
                        {
                            "filename": uploaded_file.name,
                            "status": "error",
                            "detail": str(exc),
                        }
                    )

            render_ingestion_results(results)


def render_main_area():
    st.title("AI Engineering Knowledge Assistant")
    st.caption("Grounded answers from your own engineering documents.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    if not st.session_state.messages:
        st.info(
            "Ask a question such as: "
            "*What is the scheduled airflow capacity of the HVAC unit serving Project Alpha?*"
        )

    question = st.chat_input("Ask an engineering question")

    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    try:
        chunks = Retriever().retrieve(question)
    except Exception:
        st.error("Retrieval failed. Check that PostgreSQL and Ollama are available.")
        return

    if not chunks:
        st.warning(
            "No indexed content was found. Ingest the demo documents or upload a file from the sidebar."
        )
        return

    try:
        answer = Generator().generate(question, chunks)
    except Exception:
        st.error(
            "The model could not generate an answer. Check that Ollama is running and the configured model is available."
        )
        return

    with st.chat_message("assistant"):
        st.markdown(answer)
        render_sources(chunks)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": chunks,
        }
    )


def render_sidebar():
    st.sidebar.title("Engineering RAG")
    render_service_status()
    render_ingestion_controls()

    if st.sidebar.button("Warm up model"):
        with st.spinner("Warming up the model..."):
            from app.llm.chat import ChatService

            elapsed = ChatService().warm_up()
        st.sidebar.success(f"Model warm-up: {elapsed} s")

    if st.sidebar.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()


st.set_page_config(
    page_title="AI Engineering Knowledge Assistant",
    page_icon="📚",
    layout="wide",
)

render_sidebar()
render_main_area()
