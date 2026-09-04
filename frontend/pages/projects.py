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

    # Security Warning
    st.warning("⚠️ **Warning:** BugForge will execute code from this project on your local computer. Only analyze and run projects that you trust.")
    confirm_exec = st.checkbox("I understand and confirm that I trust local project execution on this machine.")

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
                        
                        entry_point = st.text_input(f"Entry File for Project #{proj['id']}", value="main.py", key=f"entry_{proj['id']}")
                        
                        col1, col2 = st.columns(2)
                        if col1.button("Scan Project", key=f"scan_{proj['id']}"):
                            try:
                                scan_res = requests.post(f"{API_URL}/projects/{proj['id']}/scan")
                                if scan_res.status_code == 200:
                                    data = scan_res.json()
                                    st.success(f"Found {data['files_found']} Python files. Identified entry points: {data['entry_points']}")
                                else:
                                    st.error(f"Scan failed: {scan_res.text}")
                            except Exception as e:
                                st.error(f"Error scanning project: {e}")

                        if col2.button("Run Project Entrypoint", key=f"run_{proj['id']}"):
                            if not confirm_exec:
                                st.error("Execution blocked: You must confirm the execution safety warning above before running code.")
                            else:
                                try:
                                    with st.spinner("Executing Python script locally..."):
                                        run_res = requests.post(
                                            f"{API_URL}/projects/{proj['id']}/run",
                                            json={"entry_point": entry_point}
                                        )
                                    if run_res.status_code == 200:
                                        result = run_res.json()
                                        if result.get("timed_out"):
                                            st.error("Execution Timed Out!")
                                        elif result.get("exit_code") == 0:
                                            st.success("Execution completed successfully!")
                                        else:
                                            st.warning(f"Execution finished with exit code {result.get('exit_code')}")

                                        if result.get("stdout"):
                                            st.subheader("stdout")
                                            st.code(result["stdout"])
                                        if result.get("stderr"):
                                            st.subheader("stderr")
                                            st.code(result["stderr"])
                                    else:
                                        st.error(f"Run failed: {run_res.text}")
                                except Exception as e:
                                    st.error(f"Error running project: {e}")
        else:
            st.error("Failed to load projects from backend API.")
    except Exception as e:
        st.warning("Backend API is currently offline. Start the backend to view project data.")
