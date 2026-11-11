"""AI Assistant view: modern chat experience on top of the existing RAG workflow."""

import streamlit as st

from app.health import model_ready, ollama_health
from app.llm.chat import ChatService, resolve_model
from app.retrieval.generator import Generator
from app.retrieval.prompts import REFUSAL_MESSAGE
from app.retrieval.retriever import Retriever
from app.ui.components import (
    copy_button,
    display_model_name,
    esc,
    page_header,
    pill,
    refusal_banner,
    render_source_cards,
)

USER_AVATAR = "🧑‍🔧"
ASSISTANT_AVATAR = "🤖"

NO_CONTENT_NOTE = (
    "I could not find any indexed content related to this question. "
    "Ingest the demonstration documents or upload your own files first."
)

SUGGESTED_PROMPTS = [
    {
        "domain": "HVAC",
        "label": "Find HVAC specifications",
        "question": "What are the HVAC equipment specifications for Project Alpha, including scheduled airflow capacities?",
    },
    {
        "domain": "Electrical",
        "label": "Identify electrical equipment dependencies",
        "question": "Which electrical panels supply the mechanical and plumbing equipment in Project Alpha?",
    },
    {
        "domain": "Plumbing",
        "label": "Retrieve plumbing equipment information",
        "question": "What plumbing equipment is installed in Project Alpha and what are its scheduled flow rates?",
    },
    {
        "domain": "Commissioning",
        "label": "Summarize commissioning requirements",
        "question": "Summarize the commissioning requirements for Project Alpha.",
    },
]

WELCOME_ICON_SVG = """
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="13" cy="13" r="8" stroke="#16B8A6" stroke-width="2.2" fill="none"/>
  <path d="M19 19 L25 25" stroke="#3182CE" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M10 13 H16 M13 10 V16" stroke="#3182CE" stroke-width="1.8" stroke-linecap="round"/>
</svg>
"""


def render_model_banner() -> None:
    model_raw = resolve_model()
    model_name = display_model_name(model_raw)
    ollama_ok = ollama_health()

    if not ollama_ok:
        readiness = pill("Offline", "error")
        detail = "Ollama is not reachable from this application."
        local_note = "Connection status unknown"
    elif model_ready():
        readiness = pill("Ready", "success")
        detail = "Model loaded in Ollama memory · Local inference"
        local_note = "Local inference"
    else:
        readiness = pill("Warming up", "warning")
        detail = "First request may take 10–15 seconds while the model loads."
        local_note = "Local inference"

    st.markdown(
        '<div class="eip-model-banner">'
        '<div class="eip-model-chip">🤖</div>'
        "<div style=\"flex:1;min-width:180px\">"
        f'<div class="eip-model-name">{esc(model_name)} · {esc(local_note)}</div>'
        f'<div class="eip-model-detail">{esc(detail)}</div>'
        "</div>"
        f"<div>{readiness}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("Warm up model", key="assistant-warmup", type="tertiary"):
        with st.spinner("Loading the model into memory…"):
            elapsed = ChatService().warm_up()
        st.success(f"Model warm-up complete in {elapsed} s — the assistant is ready.")

    header_left, header_right = st.columns([4, 1])
    with header_right:
        if st.button("＋ New conversation", key="assistant-new", type="tertiary", use_container_width=True):
            confirm_new_conversation()


def render_welcome() -> None:
    st.markdown(
        '<div class="eip-welcome">'
        f'<div class="eip-welcome-icon">{WELCOME_ICON_SVG}</div>'
        "<h2>Engineering AI Assistant</h2>"
        '<div class="eip-welcome-desc">Ask questions about your engineering documents. '
        "Every answer is grounded in retrieved source material with numbered citations — "
        "and the assistant clearly says so when the knowledge base does not contain "
        "the information you need.</div>"
        '<div class="eip-welcome-capabilities">'
        f'<span class="eip-pill eip-pill-info"><span class="eip-dot"></span>Grounded citations</span>'
        f'<span class="eip-pill eip-pill-success"><span class="eip-dot"></span>Deterministic refusals</span>'
        f'<span class="eip-pill eip-pill-neutral"><span class="eip-dot"></span>Source excerpts</span>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    left_pair = SUGGESTED_PROMPTS[:2]
    right_pair = SUGGESTED_PROMPTS[2:]

    for row_pair in (left_pair, right_pair):
        columns = st.columns(2)
        for column, prompt in zip(columns, row_pair):
            with column:
                st.markdown(
                    '<div class="eip-suggested">'
                    f'<span class="eip-suggested-domain">{esc(prompt["domain"])}</span>'
                    f'<div class="eip-suggested-question">{esc(prompt["question"])}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Ask this question →",
                    key=f"suggest-{prompt['domain'].lower()}",
                    type="tertiary",
                    use_container_width=True,
                ):
                    st.session_state["assistant_pending"] = prompt["question"]
                    st.rerun()

    # Streamlit auto-scrolls the app container toward the chat input on load.
    # On the welcome screen the conversation starter belongs at the top, so a
    # short-lived guard scrolls back up. It stops by itself and never runs in
    # runs that render a conversation (render_welcome is skipped there).
    st.html(
        """
        <script>
        (function() {
          var ticks = 0;
          var timer = setInterval(function() {
            ticks += 1;
            var main = document.querySelector('main');
            if (main && main.scrollTop > 0) {
              try { main.scrollTo({ top: 0, behavior: "auto" }); } catch (err) { main.scrollTop = 0; }
            }
            if (ticks >= 15) { clearInterval(timer); }
          }, 150);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_assistant_content(message: dict, actions: bool) -> None:
    if message.get("refused"):
        refusal_banner()

    st.markdown(message["content"])

    if message.get("kind") == "no-content":
        return

    render_source_cards(message.get("sources") or [])

    if actions:
        copy_button(message["content"], label="Copy answer")
        if st.button("↻ Regenerate answer", key="assistant-regenerate", type="tertiary"):
            st.session_state["assistant_regenerate"] = True
            st.rerun()


@st.dialog("Start a new conversation?", width="small")
def confirm_new_conversation() -> None:
    st.write(
        "This removes all messages from the current session. "
        "The knowledge base is not affected."
    )
    left, right = st.columns(2)
    if right.button("New conversation", type="primary", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    if left.button("Keep conversation", use_container_width=True):
        st.rerun()


def render_history(messages: list[dict]) -> None:
    for index, message in enumerate(messages):
        is_latest = index == len(messages) - 1
        avatar = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR

        with st.chat_message(message["role"], avatar=avatar):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                render_assistant_content(message, actions=is_latest)


def handle_question(question: str, messages: list[dict], regenerate: bool = False) -> bool:
    """Run the RAG workflow and append messages to history.

    Returns True when an assistant message was appended. The caller decides
    whether to rerun so the history loop renders the finished exchange with
    correct per-message actions; failed runs return False so error messages
    stay visible.
    """
    if not regenerate:
        messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(question)

    try:
        with st.status("Searching the knowledge base…", expanded=False) as status:
            st.write("Embedding the question and searching the FAISS vector index.")
            chunks = Retriever().retrieve(question)

            if not chunks:
                status.update(label="No indexed content found", state="error")
                messages.append(
                    {
                        "role": "assistant",
                        "content": NO_CONTENT_NOTE,
                        "sources": [],
                        "kind": "no-content",
                    }
                )
                return True

            st.write(f"Retrieved {len(chunks)} relevant document chunks.")
            status.update(label=f"Found {len(chunks)} relevant sources", state="complete")
    except Exception:
        st.error(
            "Retrieval failed. The knowledge base is unreachable — check that "
            "PostgreSQL and Ollama are available, then try again."
        )
        return False

    try:
        with st.status("Generating a grounded answer…", expanded=False) as status:
            st.write(f"Answering with {display_model_name(resolve_model())} using the retrieved context only.")
            answer = Generator().generate(question, chunks)
            status.update(label="Answer complete", state="complete")
    except Exception:
        st.error(
            "The model could not generate an answer. Check that Ollama is running "
            "and the configured model is available, then try again."
        )
        return False

    refused = is_refusal(answer)
    content = REFUSAL_MESSAGE if refused else strip_trailing_refusal_echo(answer)

    messages.append(
        {
            "role": "assistant",
            "content": content,
            "sources": chunks,
            "refused": refused,
        }
    )
    return True


def is_refusal(answer: str) -> bool:
    """True only when the answer itself is the deterministic refusal.

    The model sometimes echoes the refusal phrase after a substantive answer;
    that echo is not a refusal.
    """
    stripped = (answer or "").strip()
    return stripped == REFUSAL_MESSAGE or stripped.startswith(REFUSAL_MESSAGE)


def strip_trailing_refusal_echo(answer: str) -> str:
    """Remove the refusal phrase when the model appends it after a real answer."""
    stripped = (answer or "").strip()

    if (
        stripped.endswith(REFUSAL_MESSAGE)
        and len(stripped) > len(REFUSAL_MESSAGE) + 40
    ):
        trimmed = stripped[: -len(REFUSAL_MESSAGE)].rstrip()
        if trimmed.endswith(("—", "-", "·")):
            trimmed = trimmed[:-1].rstrip()
        return trimmed

    return stripped


def view() -> None:
    page_header("AI Assistant", "Grounded engineering answers with source citations")

    render_model_banner()

    messages = st.session_state.setdefault("messages", [])

    # Regeneration must drop the old answer before the history renders.
    regenerating = False
    if st.session_state.pop("assistant_regenerate", False):
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            None,
        )
        if last_user and messages and messages[-1]["role"] == "assistant":
            messages.pop()
            regenerating = True
            st.session_state["assistant_last_user"] = last_user

    pending = st.session_state.pop("assistant_pending", None)
    scroll_to_latest = st.session_state.pop("assistant_scroll_to_latest", False)

    render_history(messages)

    if not messages and not pending and not regenerating:
        render_welcome()

    if scroll_to_latest:
        # After a completed exchange the view jumps to the newest message.
        # The guard stops by itself so normal scrolling resumes immediately.
        st.html(
            """
            <script>
            (function() {
              var ticks = 0;
              var timer = setInterval(function() {
                ticks += 1;
                var main = document.querySelector('main');
                if (main) {
                  try { main.scrollTo({ top: main.scrollHeight, behavior: "auto" }); } catch (err) { main.scrollTop = main.scrollHeight; }
                }
                if (ticks >= 15) { clearInterval(timer); }
              }, 150);
            })();
            </script>
            """,
            unsafe_allow_javascript=True,
        )

    def process(question: str, regenerate: bool = False) -> None:
        if handle_question(question, messages, regenerate=regenerate):
            st.session_state["assistant_scroll_to_latest"] = True
            st.rerun()

    if pending:
        process(pending)

    if regenerating:
        stored_question = st.session_state.pop("assistant_last_user", None)
        if stored_question:
            process(stored_question, regenerate=True)

    question = st.chat_input("Ask an engineering question…")

    if question and question.strip():
        process(question.strip())
    elif question is not None:
        st.warning("Please enter a question before sending.")
