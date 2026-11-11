"""Ingestion Pipelines view: run and monitor the real ingestion pipeline."""

from datetime import datetime

import streamlit as st

from app.ingestion.pipeline import IngestionPipeline
from app.ui.components import (
    DEMO_DATA_DIR,
    border_panel,
    empty_state,
    esc,
    html_panel,
    ingest_uploaded_files,
    info_row,
    metric_card,
    metric_row,
    page_header,
    pill,
    supported_upload_types,
)

RESULT_LABELS = {
    "ingested": ("✅ Ingested", "success"),
    "skipped": ("⏭ Skipped", "info"),
    "error": ("❌ Failed", "error"),
}


def _record_run(source: str, results: list[dict]) -> None:
    st.session_state["pipeline_runs"].append(
        {
            "source": source,
            "at": datetime.now(),
            "results": results,
        }
    )


def run_demo_pipeline() -> None:
    with st.status("Running the ingestion pipeline…", expanded=False) as status:
        st.write("Processing the synthetic demonstration document set.")
        results = IngestionPipeline().ingest_directory(DEMO_DATA_DIR)
        status.update(label=f"Pipeline finished — {len(results)} file(s) processed", state="complete")

    _record_run("Demo document set", results)


def run_upload_pipeline(uploaded_files) -> None:
    with st.status("Running the ingestion pipeline…", expanded=False) as status:
        st.write(f"Processing {len(uploaded_files)} uploaded file(s).")
        results = ingest_uploaded_files(uploaded_files)
        status.update(label=f"Pipeline finished — {len(results)} file(s) processed", state="complete")

    _record_run("Custom upload", results)


def render_pipeline_entry() -> None:
    left, right = st.columns(2)

    with left:
        with border_panel("pipeline-demo"):
            st.markdown(
                '<div class="eip-panel-title">'
                '<span class="eip-panel-icon">🧪</span><span>Demo document set</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.78rem;color:var(--eip-text-2);line-height:1.5;">'
                "Five synthetic MEP documents for the fictional Project Alpha: HVAC, electrical and "
                "plumbing specifications, an equipment register, and a commissioning summary. "
                "Running again is safe — already-ingested documents are skipped.</div>",
                unsafe_allow_html=True,
            )
            if st.button("Run demo ingestion", key="pipeline-run-demo", type="primary", use_container_width=True):
                run_demo_pipeline()
                st.rerun()

    with right:
        with border_panel("pipeline-upload"):
            st.markdown(
                '<div class="eip-panel-title">'
                '<span class="eip-panel-icon">📤</span><span>Custom upload</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.78rem;color:var(--eip-text-2);line-height:1.5;">'
                "Upload your own supported documents "
                f"({esc(', '.join(supported_upload_types()).upper())}) and run them through the "
                "same idempotent pipeline.</div>",
                unsafe_allow_html=True,
            )
            uploaded_files = st.file_uploader(
                "Select documents",
                type=supported_upload_types(),
                accept_multiple_files=True,
                key="pipeline-uploads",
            )
            if st.button(
                "Run upload ingestion",
                key="pipeline-run-uploads",
                type="primary",
                use_container_width=True,
                disabled=not uploaded_files,
            ):
                run_upload_pipeline(uploaded_files)
                st.rerun()


def _summary_counts(results: list[dict]) -> tuple[int, int, int]:
    processed = sum(1 for r in results if r["status"] == "ingested")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "error")
    return processed, skipped, failed


def render_last_run(run: dict | None) -> None:
    if run is None:
        empty_state(
            "⚙",
            "No ingestion runs in this session yet",
            "Run the demo document set or upload files above. Results, counts, and the "
            "run timestamp will appear here.",
        )
        return

    processed, skipped, failed = _summary_counts(run["results"])
    timestamp = run["at"].strftime("%b %d, %Y · %H:%M:%S") if isinstance(run["at"], datetime) else str(run["at"])

    summary = (
        '<div class="eip-metric-grid">'
        + metric_card("Processed", str(processed), "Newly ingested documents", "✅")
        + metric_card("Skipped", str(skipped), "Already in the knowledge base", "⏭")
        + metric_card("Failed", str(failed), "Errors during processing", "❌")
        + "</div>"
    )

    header_row = "<tr><th>File</th><th>Status</th><th>Message</th></tr>"
    body_rows = []
    for result in run["results"]:
        label, kind = RESULT_LABELS[result["status"]]
        message = result["detail"] or (
            "Already ingested — not duplicated" if result["status"] == "skipped" else "—"
        )
        body_rows.append(
            "<tr>"
            f'<td class="eip-cell-strong">{esc(result["filename"])}</td>'
            f"<td>{pill(label, kind)}</td>"
            f'<td class="eip-cell-muted">{esc(message)}</td>'
            "</tr>"
        )

    results_table = (
        f'<table class="eip-table"><thead>{header_row}</thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table>"
    )

    footer = (
        f'<div class="eip-cell-muted" style="font-size:0.72rem;color:var(--eip-text-2);'
        f'margin-top:0.5rem;">Run completed {esc(timestamp)} · Source: {esc(run["source"])}</div>'
    )

    html_panel("Last run", summary + results_table + footer, icon="📊")


def render_history(runs: list[dict]) -> None:
    with st.expander("Session run history", expanded=False):
        for run in reversed(runs[:-1]):
            processed, skipped, failed = _summary_counts(run["results"])
            timestamp = (
                run["at"].strftime("%b %d, %Y · %H:%M:%S") if isinstance(run["at"], datetime) else str(run["at"])
            )
            st.markdown(
                info_row(
                    f"{run['source']} — {timestamp}",
                    f"{processed} ingested · {skipped} skipped · {failed} failed",
                ),
                unsafe_allow_html=True,
            )
        if len(runs) <= 1:
            st.caption("Previous runs from this session will be listed here.")


def view() -> None:
    page_header("Ingestion Pipelines", "Run and monitor document ingestion")

    st.session_state.setdefault("pipeline_runs", [])
    runs = st.session_state["pipeline_runs"]

    render_pipeline_entry()

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    render_last_run(runs[-1] if runs else None)

    render_history(runs)
