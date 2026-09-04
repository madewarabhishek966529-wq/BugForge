import streamlit as st

st.set_page_config(
    page_title="BugForge - AI Bug Detection & Debugging Platform",
    page_icon="🛠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
st.sidebar.title("🛠 BugForge")
st.sidebar.caption("AI-Powered Bug Detection Platform v1.0")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Projects", "Bug Explorer", "Runtime Logs", "Settings"]
)

if page == "Dashboard":
    from frontend.pages import dashboard
    dashboard.render()
elif page == "Projects":
    from frontend.pages import projects
    projects.render()
elif page == "Bug Explorer":
    from frontend.pages import bug_explorer
    bug_explorer.render()
elif page == "Runtime Logs":
    from frontend.pages import runtime_logs
    runtime_logs.render()
elif page == "Settings":
    from frontend.pages import settings
    settings.render()
