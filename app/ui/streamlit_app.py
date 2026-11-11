"""Engineering Intelligence Platform — application entry point.

Navigation is Streamlit-native (``st.navigation`` with hidden auto-nav) so the
sidebar can carry the product brand above a custom nav; page switching uses
``st.page_link`` with real client-side routing that preserves session state.
"""

import streamlit as st

from app.ui.components import brand_header, sidebar_footer, sidebar_service_status
from app.ui.styles import load_css
from app.ui.views import assistant, knowledge_base, overview, pipelines
from app.ui.views import settings as settings_view

st.set_page_config(
    page_title="Engineering Intelligence Platform",
    page_icon="🛠",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

overview_page = st.Page(
    overview.view,
    title="Overview",
    icon=":material/space_dashboard:",
    url_path="overview",
    default=True,
)
assistant_page = st.Page(
    assistant.view,
    title="AI Assistant",
    icon=":material/forum:",
    url_path="ai-assistant",
)
knowledge_page = st.Page(
    knowledge_base.view,
    title="Knowledge Base",
    icon=":material/folder_open:",
    url_path="knowledge-base",
)
pipelines_page = st.Page(
    pipelines.view,
    title="Ingestion Pipelines",
    icon=":material/account_tree:",
    url_path="ingestion-pipelines",
)
settings_page = st.Page(
    settings_view.view,
    title="System Settings",
    icon=":material/settings:",
    url_path="system-settings",
)

PAGES = [overview_page, assistant_page, knowledge_page, pipelines_page, settings_page]

st.session_state["eip_pages"] = {
    "overview": overview_page,
    "assistant": assistant_page,
    "knowledge": knowledge_page,
    "pipelines": pipelines_page,
    "settings": settings_page,
}

current = st.navigation(PAGES, position="hidden")

NAV_ITEMS = [
    (overview_page, "Overview", "Overview", ":material/space_dashboard:"),
    (assistant_page, "AI Assistant", "AI Assistant", ":material/forum:"),
    (knowledge_page, "Knowledge Base", "Knowledge Base", ":material/folder_open:"),
    (pipelines_page, "Ingestion Pipelines", "Ingestion Pipelines", ":material/account_tree:"),
    (settings_page, "System Settings", "System Settings", ":material/settings:"),
]

with st.sidebar:
    brand_header()

    st.markdown('<div class="eip-sidebar-caption">Navigation</div>', unsafe_allow_html=True)

    for page, label, active_label, icon in NAV_ITEMS:
        if page is current:
            st.page_link(
                page,
                label=f"● {active_label}",
                icon=icon,
                use_container_width=True,
            )
        else:
            st.page_link(page, label=label, icon=icon, use_container_width=True)

    sidebar_service_status(compact=True)
    sidebar_footer()

current.run()
