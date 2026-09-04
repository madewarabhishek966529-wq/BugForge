import streamlit as st

def render():
    st.title("BUGFORGE")
    st.subheader("AI-Powered Bug Detection & Debugging Platform")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Bugs", "0")
    with col2:
        st.metric("Critical Bugs", "0", delta_color="inverse")
    with col3:
        st.metric("High Severity", "0", delta_color="inverse")
    with col4:
        st.metric("Medium Severity", "0")
    with col5:
        st.metric("Low Severity", "0")

    st.markdown("---")
    st.info("👋 Welcome to BugForge V1.0 MVP! Select a page from the sidebar navigation to get started.")
