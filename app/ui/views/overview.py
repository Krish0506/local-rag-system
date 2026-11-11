"""Overview dashboard: real platform metrics, activity, and navigation."""

from datetime import datetime

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings
from app.health import database_health, knowledge_base_counts, model_ready, ollama_health
from app.storage.faiss_store import FAISSStore
from app.storage.postgres import SessionLocal
from app.storage.repository import Repository
from app.ui.components import (
    display_model_name,
    esc,
    health_pill,
    html_panel,
    info_row,
    metric_card,
    metric_row,
    page_header,
    pill,
    quick_nav_row,
)

SUGGESTED_QUERIES = [
    ("What is the scheduled airflow capacity of the HVAC unit serving Project Alpha?", "HVAC"),
    ("Which electrical panel supplies the mechanical equipment in Project Alpha?", "Electrical"),
    ("What plumbing equipment is installed in Project Alpha and what are its scheduled flow rates?", "Plumbing"),
    ("Summarize the commissioning requirements for Project Alpha.", "Commissioning"),
]


def _load_documents() -> list[dict] | None:
    session = SessionLocal()
    try:
        return Repository(session).list_documents_with_chunk_counts()
    except (SQLAlchemyError, OSError):
        return None
    finally:
        session.close()


def render_metrics(documents: list[dict] | None, db_ok: bool, ollama_ok: bool) -> tuple[int, int, int]:
    document_count = len(documents) if documents is not None else 0
    chunk_count = sum(doc["chunk_count"] for doc in documents) if documents is not None else 0

    try:
        store = FAISSStore()
        vector_count = store.index.ntotal
        vector_dimension = store.index.d
        vector_ok = True
    except Exception:
        vector_count = None
        vector_dimension = None
        vector_ok = False

    db_value = "Connected" if db_ok else "Unavailable"
    db_kind = "ok" if db_ok else "bad"

    metric_row(
        [
            metric_card("Total documents", f"{document_count}", "Indexed in PostgreSQL", "📄"),
            metric_card("Indexed chunks", f"{chunk_count}", "Retrieval-ready text chunks", "🧩"),
            metric_card(
                "Vector index",
                f"{vector_count}" if vector_ok else "Unavailable",
                f"{vector_dimension}-dim FAISS index" if vector_ok else "Index could not be loaded",
                "🧭",
            ),
            metric_card(
                "Active AI model",
                display_model_name(settings.LLM_MODEL),
                f"Fallback: {display_model_name(settings.LLM_FALLBACK_MODEL)}",
                "🤖",
            ),
        ]
    )

    metric_row(
        [
            metric_card("PostgreSQL", db_value, "Metadata and document registry", "🗄", kind=db_kind),
            metric_card(
                "Ollama",
                "Connected" if ollama_ok else "Unavailable",
                "Local model inference service",
                "⚡",
                kind="ok" if ollama_ok else "bad",
            ),
        ]
    )

    return chunk_count, vector_count or 0, vector_ok


def render_knowledge_summary(documents: list[dict] | None) -> None:
    if not documents:
        body = (
            info_row("Status", "No documents ingested yet")
            + info_row("Next step", "Ingest documents from the Knowledge Base page")
        )
    else:
        type_counts: dict[str, int] = {}
        for document in documents:
            ext = (document.get("document_type") or "").lstrip(".").upper() or "N/A"
            type_counts[ext] = type_counts.get(ext, 0) + 1

        body = "".join(
            info_row(f"{ext} documents", str(count)) for ext, count in sorted(type_counts.items())
        )

    html_panel("Knowledge base summary", body, icon="📚")


def render_recent_activity(documents: list[dict] | None) -> None:
    if documents is None:
        body = info_row("Status", "Database unavailable — activity cannot be shown")
        html_panel("Recent ingestion activity", body, icon="🕘")
        return

    if not documents:
        body = (
            '<div style="font-size:0.8rem;color:var(--eip-text-2);padding:0.3rem 0;">'
            "No ingestion activity yet. Documents you ingest will appear here with "
            "their actual timestamps.</div>"
        )
        html_panel("Recent ingestion activity", body, icon="🕘")
        return

    rows = []
    for document in documents[:5]:
        created = document.get("created_at")
        if isinstance(created, datetime):
            created_text = created.strftime("%b %d, %Y · %H:%M")
        else:
            created_text = str(created or "—")
        rows.append(info_row(document.get("filename", "—"), created_text))

    html_panel("Recent ingestion activity", "".join(rows), icon="🕘")


def render_readiness(documents: list[dict] | None, chunk_count: int, vector_count: int) -> None:
    db_ok = database_health()
    ollama_ok = ollama_health()

    try:
        model_loaded = model_ready()
    except Exception:
        model_loaded = False

    if documents is not None and vector_count == chunk_count:
        sync_pill = pill("In sync", "success")
    elif documents is None:
        sync_pill = pill("Unknown", "neutral")
    else:
        sync_pill = pill("Out of sync", "error")

    model_pill = (
        pill("Loaded", "success") if model_loaded else pill("Not loaded", "warning")
    )

    body = (
        f'<div class="eip-row"><span class="eip-row-label">Database connection</span>{health_pill(db_ok)}</div>'
        f'<div class="eip-row"><span class="eip-row-label">Ollama service</span>{health_pill(ollama_ok)}</div>'
        f'<div class="eip-row"><span class="eip-row-label">Index / database sync</span>{sync_pill}</div>'
        f'<div class="eip-row"><span class="eip-row-label">Chat model in memory</span>{model_pill}</div>'
    )
    html_panel("System readiness", body, icon="🩺")


def render_quick_navigation() -> None:
    quick_nav_row(
        [
            ("assistant", "💬", "AI Assistant", "Ask grounded engineering questions"),
            ("knowledge", "📚", "Knowledge Base", "Browse indexed documents"),
            ("pipelines", "⚙", "Ingestion Pipelines", "Run and monitor ingestion"),
            ("settings", "🛠", "System Settings", "Configuration and health"),
        ]
    )


def render_suggested_queries() -> None:
    st.markdown(
        '<div class="eip-panel-title" style="margin:1.1rem 0 0.55rem 0;">'
        '<span class="eip-panel-icon">🔎</span><span>Suggested engineering queries</span></div>',
        unsafe_allow_html=True,
    )

    for row_pair in (SUGGESTED_QUERIES[:2], SUGGESTED_QUERIES[2:]):
        columns = st.columns(2)
        for column, (question, domain) in zip(columns, row_pair):
            with column:
                column.markdown(
                    '<div class="eip-suggested">'
                    f'<span class="eip-suggested-domain">{esc(domain)}</span>'
                    f'<div class="eip-suggested-question" style="margin-top:0.4rem;">{esc(question)}</div>'
                    '<div class="eip-suggested-ask">Open in AI Assistant →</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
                if column.button(
                    f"Ask: {domain}",
                    key=f"overview-query-{domain.lower()}",
                    type="tertiary",
                    use_container_width=True,
                ):
                    st.session_state["assistant_pending"] = question
                    st.switch_page(st.session_state["eip_pages"]["assistant"])


def view() -> None:
    page_header("Overview", "AI-powered engineering knowledge and project intelligence")

    documents = _load_documents()
    db_ok = database_health()
    ollama_ok = ollama_health()

    if documents is None and db_ok:
        st.warning("The document list could not be loaded even though the database is reachable.")
    elif documents is None:
        st.error("PostgreSQL is unavailable. Platform data cannot be displayed.")

    chunk_count, vector_count, _ = render_metrics(documents, db_ok, ollama_ok)

    left, right = st.columns([1.15, 1])
    with left:
        render_knowledge_summary(documents)
        render_recent_activity(documents)
    with right:
        render_readiness(documents, chunk_count, vector_count)
        render_suggested_queries()

    render_quick_navigation()
