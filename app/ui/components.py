"""Reusable UI components for the Engineering Intelligence Platform.

Components render the design system defined in ``app.ui.styles``. All
dynamic values are HTML-escaped before interpolation. Every interactive
control here wraps a real Streamlit callback or existing backend call.
"""

import json
import time
import uuid
from contextlib import contextmanager
from html import escape
from pathlib import Path

import streamlit as st

from app.config.settings import PROJECT_ROOT, settings
from app.health import database_health, knowledge_base_counts, ollama_health
from app.ingestion.parser import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import IngestionPipeline
from app.storage.faiss_store import FAISSStore

DEMO_DATA_DIR = PROJECT_ROOT / "demo_data"

_BLURB_LINE = "AI-powered engineering knowledge and project intelligence"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def esc(value) -> str:
    return escape(str(value if value is not None else ""))


_MODEL_DISPLAY_ALIASES = {
    "qwen3.5": "Qwen 3.5",
    "mistral": "Mistral",
    "bge-m3": "BGE-M3",
}


def display_model_name(raw: str) -> str:
    """Convert a raw Ollama model tag such as ``qwen3.5:4b`` into a display name."""
    if not raw:
        return "Unknown model"

    name = str(raw).split("@", 1)[0]
    base, _, size = name.partition(":")

    base_display = _MODEL_DISPLAY_ALIASES.get(base.lower())
    if base_display is None:
        base_display = " ".join(
            part[:1].upper() + part[1:] for part in base.split("-") if part
        )

    if size and size.lower() != "latest":
        size = size.replace("-", " ")
        size = " ".join(
            part.upper() if len(part) <= 2 else part.capitalize() for part in size.split()
        )
        return f"{base_display} {size}"

    return base_display


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def pill(label: str, kind: str = "neutral") -> str:
    """Return a status pill as HTML. kind: success | warning | error | info | neutral."""
    return (
        f'<span class="eip-pill eip-pill-{esc(kind)}">'
        f'<span class="eip-dot"></span>{esc(label)}</span>'
    )


def health_pill(ok: bool, ok_label: str = "Connected", fail_label: str = "Unavailable") -> str:
    return pill(ok_label if ok else fail_label, "success" if ok else "error")


def metric_card(label: str, value: str, sublabel: str = "", icon: str = "", kind: str = "") -> str:
    value_class = f" eip-value-{kind}" if kind in {"ok", "bad"} else ""
    sub = f'<div class="eip-metric-sub">{esc(sublabel)}</div>' if sublabel else ""
    icon_html = f'<span class="eip-metric-icon">{esc(icon)}</span>' if icon else ""

    return (
        '<div class="eip-metric-card">'
        f'<div class="eip-metric-label">{icon_html}<span>{esc(label)}</span></div>'
        f'<div class="eip-metric-value{value_class}">{esc(value)}</div>'
        f"{sub}"
        "</div>"
    )


def metric_row(cards: list[str]) -> None:
    st.markdown(
        f'<div class="eip-metric-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        '<div class="eip-page-header">'
        '<div class="eip-page-accent"></div>'
        "<div>"
        f"<h1>{esc(title)}</h1>"
        f'<div class="eip-page-subtitle">{esc(subtitle)}</div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, hint: str) -> None:
    st.markdown(
        '<div class="eip-empty">'
        f'<div class="eip-empty-icon">{esc(icon)}</div>'
        f'<div class="eip-empty-title">{esc(title)}</div>'
        f'<div class="eip-empty-hint">{esc(hint)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


@contextmanager
def border_panel(key: str):
    """Context manager for panels containing native Streamlit widgets.

    The ``key`` becomes a ``st-key-<key>`` CSS class on the container, which
    ``app.ui.styles`` targets to apply the panel design (Streamlit 1.67 renders
    bordered containers without a stable ``data-testid`` hook).
    """
    with st.container(border=True, key=f"eip-panel-{key}"):
        yield

def html_panel(title: str, body_html: str, icon: str = "") -> None:
    """Render a complete static panel (title + body) in one markdown fragment.

    Because Streamlit renders each element as a sibling DOM node, panels that
    contain only generated HTML must be composed into a single fragment;
    panels containing native widgets should use :func:`border_panel`.
    """
    icon_html = f'<span class="eip-panel-icon">{esc(icon)}</span>' if icon else ""
    st.markdown(
        '<div class="eip-panel">'
        f'<div class="eip-panel-title">{icon_html}<span>{esc(title)}</span></div>'
        f"{body_html}"
        "</div>",
        unsafe_allow_html=True,
    )


def info_row(label: str, value: str, mono: bool = False) -> str:
    value_class = "eip-row-value eip-mono" if mono else "eip-row-value"
    return (
        '<div class="eip-row">'
        f'<span class="eip-row-label">{esc(label)}</span>'
        f'<span class="{value_class}">{esc(value)}</span>'
        "</div>"
    )


def type_tag(extension: str) -> str:
    return f'<span class="eip-type-tag">{esc(extension.lstrip(".").upper() or "N/A")}</span>'


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def switch_to(page_key: str) -> None:
    """Switch pages using the Page objects stashed by the app entry point."""
    pages = st.session_state.get("eip_pages")
    if pages and page_key in pages:
        st.switch_page(pages[page_key])


def quick_nav_row(cards: list[tuple[str, str, str, str]]) -> None:
    """cards: (page_key, icon, title, hint). Renders cards with a real button per card."""
    columns = st.columns(len(cards))
    for column, (page_key, icon, title, hint) in zip(columns, cards):
        with column:
            card_id = f"eip-quicknav-{page_key}-{uuid.uuid4().hex[:6]}"
            column.markdown(
                '<div class="eip-quicknav">'
                f'<div class="eip-quicknav-icon">{esc(icon)}</div>'
                f'<div class="eip-quicknav-title">{esc(title)}</div>'
                f'<div class="eip-quicknav-hint">{esc(hint)}</div>'
                "</div>",
                unsafe_allow_html=True,
            )
            if column.button(
                f"Open {title}",
                key=f"goto-{page_key}",
                type="tertiary",
                use_container_width=True,
            ):
                switch_to(page_key)


# ---------------------------------------------------------------------------
# Copy button (real clipboard write)
# ---------------------------------------------------------------------------

def copy_button(text: str, label: str = "Copy", key_hint: str = "") -> None:
    element_id = f"eip-copy-{uuid.uuid4().hex[:8]}"
    payload = json.dumps(text).replace("</", "<\\/")

    st.html(
        f"""
        <button class="eip-copy-btn" id="{element_id}" type="button">
            <span aria-hidden="true">⧉</span> {esc(label)}
        </button>
        <script>
        (function() {{
            var button = document.getElementById("{element_id}");
            if (!button) return;
            var text = {payload};
            var original = button.innerHTML;
            button.addEventListener("click", function() {{
                var done = function() {{
                    button.innerHTML = "✓ Copied";
                    setTimeout(function() {{ button.innerHTML = original; }}, 1600);
                }};
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(text).then(done, function() {{ fallback(); }});
                }} else {{
                    fallback();
                }}
                function fallback() {{
                    var area = document.createElement("textarea");
                    area.value = text;
                    area.style.position = "fixed";
                    area.style.opacity = "0";
                    document.body.appendChild(area);
                    area.select();
                    try {{ document.execCommand("copy"); done(); }} catch (e) {{}}
                    document.body.removeChild(area);
                }}
            }});
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
        width="stretch",
    )
    # key_hint reserved for future per-message identification.


# ---------------------------------------------------------------------------
# Assistant message rendering
# ---------------------------------------------------------------------------

def render_source_cards(sources: list[dict], header: str = "Sources") -> None:
    if not sources:
        st.markdown(
            '<div class="eip-source-item"><div class="eip-source-meta">'
            "No source excerpts were returned for this answer.</div></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="eip-sources-header">'
        f"<span>{esc(header)} · {len(sources)}</span>"
        '<span style="flex:1;height:1px;background:var(--eip-border)"></span>'
        "</div>",
        unsafe_allow_html=True,
    )

    for index, source in enumerate(sources, start=1):
        filename = source.get("filename") or "Unknown document"
        location = source.get("location")
        excerpt = (source.get("content") or "").strip()

        if excerpt and len(excerpt) > 320:
            excerpt = excerpt[:320].rstrip() + " …"
        excerpt = excerpt.replace("\n", " ") if excerpt else ""

        meta_bits = []
        if location:
            meta_bits.append(esc(location))
        if source.get("chunk_id"):
            meta_bits.append(f"chunk #{esc(source['chunk_id'])}")

        meta_html = f'<div class="eip-source-meta">{" · ".join(meta_bits)}</div>' if meta_bits else ""
        excerpt_html = (
            f'<div class="eip-source-excerpt">{esc(excerpt)}</div>' if excerpt else ""
        )

        st.markdown(
            '<div class="eip-source-item">'
            '<div class="eip-source-title">'
            f'<span class="eip-cite-badge">[{index}]</span>'
            f"<span>{esc(filename)}</span>"
            "</div>"
            f"{meta_html}"
            f"{excerpt_html}"
            "</div>",
            unsafe_allow_html=True,
        )


def refusal_banner() -> None:
    st.markdown(
        '<div class="eip-refusal-banner">⚠ '
        "Insufficient evidence in the knowledge base — no answer was invented.</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _logo_svg() -> str:
    return """
    <svg width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="36" height="36" rx="9" fill="#1D3048"/>
      <path d="M8 26 L16 12 L22 21 L26 15 L30 22" stroke="#16B8A6" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <circle cx="16" cy="12" r="1.6" fill="#3182CE"/>
      <circle cx="26" cy="15" r="1.6" fill="#3182CE"/>
      <path d="M8 30 H30" stroke="#3182CE" stroke-width="1.4" stroke-linecap="round" opacity="0.55"/>
    </svg>
    """


def brand_header() -> None:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:0.65rem;'
        'padding:0.35rem 0.1rem 0.15rem 0.1rem;">'
        f"{_logo_svg()}"
        "<div>"
        '<div class="eip-brand-name">Engineering Intelligence</div>'
        f'<div class="eip-brand-subtitle">{esc(_BLURB_LINE)}</div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def sidebar_service_status(compact: bool = True) -> None:
    db_ok = database_health()
    ollama_ok = ollama_health()

    vector_count = None
    try:
        vector_count = FAISSStore().index.ntotal
    except Exception:
        vector_count = None

    st.markdown('<div class="eip-sidebar-caption">Platform status</div>', unsafe_allow_html=True)

    vector_pill = (
        pill(f"{vector_count} vectors", "success")
        if vector_count is not None
        else pill("Unavailable", "error")
    )

    st.markdown(
        '<div class="eip-status-row"><span class="eip-status-label">PostgreSQL</span>'
        f"{health_pill(db_ok)}</div>"
        '<div class="eip-status-row"><span class="eip-status-label">Ollama</span>'
        f"{health_pill(ollama_ok)}</div>"
        '<div class="eip-status-row"><span class="eip-status-label">Vector index</span>'
        f"{vector_pill}</div>",
        unsafe_allow_html=True,
    )

    if not compact:
        try:
            documents, chunks = knowledge_base_counts()
            st.markdown(
                '<div class="eip-status-row"><span class="eip-status-label">Documents</span>'
                f'<span class="eip-status-label">{documents} docs · {chunks} chunks</span></div>',
                unsafe_allow_html=True,
            )
        except Exception:
            pass


def sidebar_footer() -> None:
    from app.config import settings as settings_module

    st.markdown(
        '<div class="eip-sidebar-footer">'
        f"<strong>Engineering Intelligence Platform</strong> v{esc(settings_module.APP_VERSION)}<br/>"
        "Local-first · PostgreSQL · FAISS · Ollama"
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Shared ingestion action (used by Knowledge Base and Pipelines views)
# ---------------------------------------------------------------------------

def ingest_uploaded_files(uploaded_files) -> list[dict]:
    """Persist uploads to RAW_DATA_DIR and run the existing idempotent pipeline."""
    target_directory = Path(settings.raw_directory)
    target_directory.mkdir(parents=True, exist_ok=True)

    pipeline = IngestionPipeline()
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

    return results


def supported_upload_types() -> list[str]:
    return sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS)
