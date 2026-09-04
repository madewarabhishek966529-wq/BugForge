import streamlit as st

def render():
    st.title("📑 Runtime Logs")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Status", "Idle")
    with col2:
        st.metric("Duration", "0.0s")
    with col3:
        st.metric("Timeout Status", "Normal")

    st.markdown("### Standard Output (stdout)")
    st.code("No execution logs captured yet.", language="text")

    st.markdown("### Standard Error (stderr)")
    st.code("No error logs captured yet.", language="text")
