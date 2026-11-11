"""Knowledge Base view: document management over the real ingestion pipeline."""

from datetime import datetime

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from app.ingestion.pipeline import IngestionPipeline
from app.storage.faiss_store import FAISSStore
from app.storage.postgres import SessionLocal
from app.storage.repository import Repository
from app.ui.components import (
    DEMO_DATA_DIR,
    empty_state,
    esc,
    info_row,
    ingest_uploaded_files,
    metric_card,
    metric_row,
    page_header,
    supported_upload_types,
    type_tag,
)

RESULT_LABELS = {
    "ingested": ("✅ Ingested", "success"),
    "skipped": ("⏭ Already ingested", "info"),
    "error": ("❌ Failed", "error"),
}


def _load_documents() -> list[dict] | None:
    session = SessionLocal()
    try:
        return Repository(session).list_documents_with_chunk_counts()
    except (SQLAlchemyError, OSError):
        return None
    finally:
        session.close()


def render_ingestion_feedback() -> None:
    results = st.session_state.pop("kb_last_ingestion", None)
    if not results:
        return

    processed = sum(1 for r in results if r["status"] == "ingested")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "error")

    if failed:
        st.error(f"Ingestion finished with {failed} failure(s): {processed} ingested, {skipped} skipped.")
    elif processed:
        st.success(f"Ingestion complete: {processed} ingested, {skipped} skipped.")
    elif skipped:
        st.info(f"All {skipped} document(s) were already ingested — nothing was duplicated.")

    with st.expander("Ingestion details", expanded=bool(failed)):
        for result in results:
            label, kind = RESULT_LABELS[result["status"]]
            detail = f" — {result['detail']}" if result["detail"] else ""
            st.markdown(
                f"{label} · **{esc(result['filename'])}**{esc(detail)}",
                unsafe_allow_html=True,
            )


def render_upload_panel(has_documents: bool) -> None:
    with st.expander("📤 Upload and ingest documents", expanded=not has_documents):
        st.caption(
            "Supported formats: PDF, DOCX, TXT, CSV, XLS, XLSX. Ingestion is idempotent — "
            "documents already in the knowledge base are skipped, never duplicated."
        )

        uploaded_files = st.file_uploader(
            "Select engineering documents",
            type=supported_upload_types(),
            accept_multiple_files=True,
        )

        left, right = st.columns(2)
        ingest_clicked = left.button(
            "Ingest uploaded files",
            key="kb-ingest-uploads",
            type="primary",
            use_container_width=True,
            disabled=not uploaded_files,
        )
        demo_clicked = right.button(
            "Ingest demo documents",
            key="kb-ingest-demo",
            use_container_width=True,
        )

        if ingest_clicked and uploaded_files:
            with st.spinner("Running the ingestion pipeline…"):
                st.session_state["kb_last_ingestion"] = ingest_uploaded_files(uploaded_files)
            st.rerun()

        if demo_clicked:
            with st.spinner("Running the ingestion pipeline on the demo document set…"):
                st.session_state["kb_last_ingestion"] = IngestionPipeline().ingest_directory(DEMO_DATA_DIR)
            st.rerun()


def render_document_table(documents: list[dict], search: str, type_filter: str) -> list[dict]:
    filtered = []
    needle = search.strip().lower()

    for document in documents:
        filename = document.get("filename", "")
        ext = (document.get("document_type") or "").lstrip(".").upper()

        if needle and needle not in filename.lower():
            continue
        if type_filter != "All types" and ext != type_filter:
            continue

        filtered.append(document)

    if not filtered:
        if documents:
            empty_state(
                "🔍",
                "No documents match your filters",
                "Adjust the search text or document type filter to see indexed documents.",
            )
        return filtered

    header_row = "<tr><th>Document</th><th>Type</th><th>Chunks</th><th>Ingested</th></tr>"
    body_rows = []
    for document in filtered:
        created = document.get("created_at")
        created_text = (
            created.strftime("%b %d, %Y · %H:%M") if isinstance(created, datetime) else str(created or "—")
        )
        ext = (document.get("document_type") or "").lstrip(".").upper()
        body_rows.append(
            "<tr>"
            f'<td class="eip-cell-strong">{esc(document.get("filename", "—"))}</td>'
            f"<td>{type_tag(ext)}</td>"
            f'<td class="eip-cell-muted">{esc(document.get("chunk_count", 0))}</td>'
            f'<td class="eip-cell-muted">{esc(created_text)}</td>'
            "</tr>"
        )

    st.markdown(
        f'<table class="eip-table"><thead>{header_row}</thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table>",
        unsafe_allow_html=True,
    )

    return filtered


def render_document_details(filtered: list[dict]) -> None:
    if not filtered:
        return

    with st.expander("📋 File details", expanded=False):
        for document in filtered:
            created = document.get("created_at")
            created_text = (
                created.strftime("%b %d, %Y · %H:%M") if isinstance(created, datetime) else str(created or "—")
            )
            ext = (document.get("document_type") or "").lstrip(".").upper()
            st.markdown(
                '<div class="eip-source-item">'
                '<div class="eip-source-title">'
                f"<span>{type_tag(ext)}</span>"
                f"<span>{esc(document.get('filename', '—'))}</span>"
                "</div>"
                "<div>"
                + info_row("Chunks indexed", str(document.get("chunk_count", 0)))
                + info_row("Source path", str(document.get("source", "—")), mono=True)
                + info_row("Ingested", created_text)
                + "</div></div>",
                unsafe_allow_html=True,
            )


def view() -> None:
    page_header("Knowledge Base", "Documents indexed for retrieval and citation")

    documents = _load_documents()

    try:
        store = FAISSStore()
        vector_count = store.index.ntotal
    except Exception:
        vector_count = None

    chunk_count = sum(doc["chunk_count"] for doc in documents) if documents else 0

    metric_row(
        [
            metric_card("Documents", f"{len(documents)}" if documents is not None else "—",
                        "In the document registry", "📄"),
            metric_card("Chunks", f"{chunk_count}", "Available for retrieval", "🧩"),
            metric_card(
                "Vector index",
                f"{vector_count}" if vector_count is not None else "—",
                "FAISS vectors",
                "🧭",
            ),
        ]
    )

    render_ingestion_feedback()

    if documents is None:
        st.error("The document list could not be loaded. PostgreSQL may be unavailable.")
        render_upload_panel(has_documents=False)
        return

    if not documents:
        empty_state(
            "📚",
            "Your knowledge base is empty",
            "Upload engineering documents below or ingest the included synthetic "
            "demonstration set to start asking grounded questions.",
        )
        render_upload_panel(has_documents=False)
        return

    render_upload_panel(has_documents=True)

    control_left, control_type, control_refresh = st.columns([2, 1, 1])
    with control_left:
        search = st.text_input(
            "Search documents",
            key="kb-search",
            placeholder="Filter by document name…",
            label_visibility="collapsed",
        )
    with control_type:
        available_types = sorted(
            {(doc.get("document_type") or "").lstrip(".").upper() or "N/A" for doc in documents}
        )
        type_filter = st.selectbox(
            "Type",
            ["All types", *available_types],
            key="kb-type-filter",
            label_visibility="collapsed",
        )
    with control_refresh:
        st.write("")  # align controls with the input row
        if st.button("↻ Refresh", key="kb-refresh", use_container_width=True):
            st.rerun()

    if search:
        st.caption(f"Showing documents matching “{search.strip()}”")

    filtered = render_document_table(documents, search, type_filter)
    render_document_details(filtered)
