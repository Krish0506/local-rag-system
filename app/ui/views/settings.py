"""System Settings view: technical configuration and health, secrets excluded."""

import streamlit as st

from app.config import settings as settings_module
from app.config.settings import settings
from app.health import database_health, loaded_models, model_ready, ollama_health
from app.llm.chat import ChatService
from app.storage.faiss_store import FAISSStore
from app.ui.components import (
    border_panel,
    display_model_name,
    health_pill,
    html_panel,
    info_row,
    page_header,
    pill,
)


def _index_info() -> tuple[int | None, int | None, str]:
    try:
        store = FAISSStore()
        return int(store.index.ntotal), int(store.index.d), str(store.index_path)
    except Exception:
        return None, None, settings.VECTOR_STORE_PATH


def view() -> None:
    page_header("System Settings", "Technical configuration and platform health")

    db_ok = database_health()
    ollama_ok = ollama_health()
    vector_count, vector_dimension, vector_path = _index_info()

    database_body = (
        f'<div class="eip-row"><span class="eip-row-label">Status</span>{health_pill(db_ok)}</div>'
        + info_row("Host", settings.POSTGRES_HOST)
        + info_row("Port", str(settings.POSTGRES_PORT))
        + info_row("Database", settings.POSTGRES_DB)
        + info_row("User", settings.POSTGRES_USER)
        + info_row("Credentials", "Managed via .env — never displayed", mono=True)
    )

    loaded = loaded_models() if ollama_ok else []
    loaded_text = ", ".join(display_model_name(name) for name in loaded) if loaded else (
        "None (models load on first use)" if ollama_ok else "Ollama unavailable"
    )

    ollama_body = (
        f'<div class="eip-row"><span class="eip-row-label">Status</span>{health_pill(ollama_ok)}</div>'
        + info_row("Endpoint", settings.OLLAMA_BASE_URL, mono=True)
        + info_row("Embedding model", f"{display_model_name(settings.EMBEDDING_MODEL)} ({settings.EMBEDDING_MODEL})", mono=True)
        + info_row("Models in memory", loaded_text)
    )

    generation_body = (
        info_row("Active chat model", display_model_name(settings.LLM_MODEL), mono=True)
        + info_row("Fallback model", display_model_name(settings.LLM_FALLBACK_MODEL), mono=True)
        + info_row("Reasoning mode", "Enabled" if settings.LLM_REASONING else "Disabled (concise grounded answers)")
        + info_row("Max answer tokens", str(settings.MAX_ANSWER_TOKENS))
        + info_row("Model context window", f"{settings.MODEL_CONTEXT_CHARS:,} characters")
    )

    retrieval_body = (
        info_row("Retrieval top-k", str(settings.RETRIEVAL_TOP_K))
        + info_row("Max context sent to model", f"{settings.MAX_CONTEXT_CHARS:,} characters")
        + info_row("Chunk size / overlap", f"{settings.CHUNK_SIZE} / {settings.CHUNK_OVERLAP} characters")
        + info_row("Vector store path", vector_path, mono=True)
        + info_row(
            "Vector index",
            f"{vector_count} vectors · {vector_dimension}-dim"
            if vector_count is not None
            else "Unavailable",
        )
    )

    application_body = (
        info_row("Application version", f"v{settings_module.APP_VERSION}")
        + info_row("Application environment", settings.APP_ENV)
        + info_row("Streamlit version", st.__version__)
        + info_row("Frontend", "Streamlit (native)")
    )

    left, right = st.columns(2)

    with left:
        html_panel("PostgreSQL", database_body, icon="🗄")
        html_panel("Ollama", ollama_body, icon="⚡")
        html_panel("Application", application_body, icon="🧱")

    with right:
        html_panel("Generation model", generation_body, icon="🤖")
        html_panel("Retrieval & vector index", retrieval_body, icon="🧭")

        with border_panel("settings-warmup"):
            st.markdown(
                '<div class="eip-panel-title">'
                '<span class="eip-panel-icon">🔥</span><span>Model warm-up</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.78rem;color:var(--eip-text-2);line-height:1.5;">'
                "Load the active chat model into Ollama memory before a demonstration so the "
                "first question returns quickly.</div>",
                unsafe_allow_html=True,
            )

            warm_clicked = st.button(
                "Warm up model now",
                key="settings-warmup",
                type="primary",
                use_container_width=True,
            )

            if warm_clicked:
                with st.spinner("Warming up the model…"):
                    elapsed = ChatService().warm_up()
                st.success(f"Model warm-up complete in {elapsed} s.")

            if ollama_ok:
                ready_pill = pill("Ready", "success") if model_ready() else pill("Not loaded", "warning")
                st.markdown(
                    f'<div class="eip-row" style="border-bottom:none;">'
                    f'<span class="eip-row-label">Current model state</span>{ready_pill}</div>',
                    unsafe_allow_html=True,
                )
