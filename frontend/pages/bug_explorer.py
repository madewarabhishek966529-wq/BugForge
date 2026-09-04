import streamlit as st
import pandas as pd

def render():
    st.title("🐞 Bug Explorer")
    st.markdown("---")

    severity_filter = st.multiselect("Filter by Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
    search_query = st.text_input("Search Bugs", placeholder="Search by error type, file, message...")

    dummy_data = pd.DataFrame(columns=["Severity", "Error", "File", "Line", "Source", "Status"])
    st.dataframe(dummy_data, use_container_width=True)
    st.info("No bugs detected yet. Scan or run a project to detect bugs.")
