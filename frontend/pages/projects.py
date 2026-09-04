import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

def render():
    st.title("📁 Projects")
    st.markdown("---")

    st.subheader("Add Local Project")
    with st.form("add_project_form"):
        project_name = st.text_input("Project Name", placeholder="e.g. My Python Service")
        project_path = st.text_input("Local Project Path", placeholder="e.g. C:/Projects/MyService")
        submitted = st.form_submit_button("Add Project")

        if submitted:
            if not project_name or not project_path:
                st.error("Please provide both project name and local path.")
            else:
                try:
                    res = requests.post(f"{API_URL}/projects", json={"name": project_name, "path": project_path})
                    if res.status_code == 201:
                        st.success(f"Project '{project_name}' added successfully!")
                    else:
                        st.error(f"Error adding project: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend API: {e}")

    st.markdown("---")
    st.subheader("Scanned Projects")
    try:
        res = requests.get(f"{API_URL}/projects")
        if res.status_code == 200:
            projects = res.json()
            if not projects:
                st.info("No projects registered yet.")
            else:
                for proj in projects:
                    with st.expander(f"📌 {proj['name']} (ID: {proj['id']})"):
                        st.write(f"**Path:** `{proj['path']}`")
                        st.write(f"**Language:** {proj['language']}")
                        st.write(f"**Created At:** {proj['created_at']}")
                        c1, c2 = st.columns(2)
                        if c1.button("Scan Project", key=f"scan_{proj['id']}"):
                            st.info("Scan initiated...")
                        if c2.button("Run Entrypoint", key=f"run_{proj['id']}"):
                            st.info("Run initiated...")
        else:
            st.error("Failed to load projects from backend.")
    except Exception as e:
        st.warning("Backend API is currently offline. Start the backend to view project data.")
